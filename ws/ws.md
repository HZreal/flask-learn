### 1 概述

socket.io是一个基于WebSocket的CS的实时通信库，它底层基于engine.io。engine.io使用WebSocket和xhr-polling(或jsonp)封装了一套自己的协议，在不支持WebSocket的低版本浏览器中(支持websocket的浏览器版本见这里)使用了长轮询(long polling)来代替。socket.io在engine.io的基础上增加了namespace，room，自动重连等特性。

本文接下来会先简单介绍websocket协议，然后在此基础上讲解下engine.io和socket.io协议以及源码分析，后续再通过例子说明socket.io的工作流程。

### 2 WebSocket协议

我们知道，在HTTP 协议开发的时候，并不是为了双向通信程序准备的，起初的 web 应用程序只需要 “请求-响应” 就够了。由于历史原因，在创建拥有双向通信机制的 web 应用程序时，就只能利用 HTTP 轮询的方式，由此产生了 “短轮询” 和 “长轮询”(注意区分短连接和长连接)。



短轮询通过客户端定期轮询来询问服务端是否有新的信息产生，缺点也是显而易见，轮询间隔大了则信息不够实时，轮询间隔过小又会消耗过多的流量，增加服务器的负担。长轮询是对短轮询的优化，需要服务端做相应的修改来支持。客户端向服务端发送请求时，如果此时服务端没有新的信息产生，并不立刻返回，而是Hang住一段时间等有新的信息或者超时再返回，客户端收到服务器的应答后继续轮询。可以看到长轮询比短轮询可以减少大量无用的请求，并且客户端接收取新消息也会实时不少。



虽然长轮询比短轮询优化了不少，但是每次请求还是都要带上HTTP请求头部，而且在长轮询的连接结束之后，服务器端积累的新消息要等到下次客户端连接时才能传递。更好的方式是只用一个TCP连接来实现客户端和服务端的双向通信，WebSocket协议正是为此而生。WebSocket是基于TCP的一个独立的协议，它与HTTP协议的唯一关系就是它的握手请求可以作为一个`Upgrade request`经由HTTP服务器解析，且与HTTP使用一样的端口。WebSocket默认对普通请求使用80端口，协议为`ws://`，对TLS加密请求使用443端口，协议为`wss://`。



握手是通过一个`HTTP Upgrade request`开始的，一个请求和响应头部示例如下(去掉了无关的头部)。WebSocket握手请求头部与HTTP请求头部是兼容的（见RFC2616）。

##Request Headers ##
Connection: Upgrade
Host: socket.io.demo.com
Origin: http://socket.io.demo.com
Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits
Sec-WebSocket-Key: mupA9l2rXciZKoMNQ9LphA==
Sec-WebSocket-Version: 13
Upgrade: websocket

\## Response Headers ##
101 Web Socket Protocol Handshake
Connection: upgrade
Sec-WebSocket-Accept: s4VAqh7eedG0a11ziQlwTzJUY3s=
Sec-WebSocket-Origin: http:
Server: nginx/1.6.2
Upgrade: WebSocket

- Upgrade 是HTTP/1.1中规定的用于转换当前连接的应用层协议的头部，表示客户端希望用现有的连接转换到新的应用层协议WebSocket协议。

- Origin 用于防止跨站攻击，浏览器一般会使用这个来标识原始域，对于非浏览器的客户端应用可以根据需要使用。

- 请求头中的 Sec-WebSocket-Version 是WebSocket版本号，Sec-WebSocket-Key 是用于握手的密钥。Sec-WebSocket-Extensions 和 Sec-WebSocket-Protocol 是可选项，暂不讨论。

- 响应头中的 Sec-WebSocket-Accept 是将请求头中的 Sec-WebSocket-Key 的值加上一个固定魔数`258EAFA5-E914-47DA-95CA-C5AB0DC85B11`经SHA1+base64编码后得到。计算过程的python代码示例（uwsgi中的实现见 core/websockets.c的 `uwsgi_websocket_handshake`函数）：

  ```
  magic_number = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
  key = 'mupA9l2rXciZKoMNQ9LphA=='
  accept = base64.b64encode(hashlib.sha1(key + ).digest())
  assert(accept == 's4VAqh7eedG0a11ziQlwTzJUY3s=')
  ```

- 客户端会检查响应头中的status code 和 Sec-WebSocket-Accept 值是否是期待的值，如果发现Accept的值不正确或者状态码不是101，则不会建立WebSocket连接，也不会发送WebSocket数据帧。



WebSocket协议使用帧（Frame）收发数据，帧格式如下。基于安全考量，**客户端发送给服务端的帧必须通过4字节的掩码（Masking-key）加密**，服务端收到消息后，用掩码对数据帧的Payload Data进行异或运算解码得到数据（详见uwsgi的 core/websockets.c 中的uwsgi_websockets_parse函数），如果服务端收到未经掩码加密的数据帧，则应该马上关闭该WebSocket。而**服务端发给客户端的数据则不需要掩码加密**，客户端如果收到了服务端的掩码加密的数据，则也必须关闭它。

0 1 2 3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+

| F | R | R | R | opcode |M| Payload len | Extended payload length |
| I | S | S | S |  (4)   | A | (7) | (16/64)|
| N | V | V | V | | S |  |  (if payload len==126/127) |
|   | 1 | 2 | 3 | | K |  |  |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
| Extended payload length continued, if payload len == 127 |

+-------------------------------+
|  | Masking-key, if MASK set to 1 |                    |
+-------------------------------+-------------------------------+
| Masking-key (continued) | Payload Data |                       |       
+-------------------------------- - - - - - - - - - - - - - - - +
: Payload Data continued ... :
+---------------------------------------------------------------+

帧分为控制帧和数据帧，控制帧不能分片，数据帧可以分片。主要字段说明如下：

- FIN: 没有分片的帧的FIN为1，分片帧的第一个分片的FIN为0，最后一个分片FIN为1。
- opcode: 帧类型编号，其中控制帧：0x8 (Close), 0x9 (Ping), and 0xA (Pong)，数据帧主要有：0x1 (Text), 0x2 (Binary)。
- MASK：客户端发给服务端的帧MASK为1，Masking-key为加密掩码。服务端发往客户端的MASK为0，Masking-key为空。
- Payload len和Payload Data分别是帧的数据长度和数据内容。

### 3 engine.io和socket.io

前面提到socket.io是基于engine.io的封装，engine.io（协议版本3）有一套自己的协议，任何engine.io服务器都必须支持polling(包括jsonp和xhr)和websocket两种传输方式。**engine.io使用websocket时有一套自己的ping/pong机制，使用的是opcode为0x1(Text)类型的数据帧，不是websocket协议规定的ping/pong类型的帧，标准的 ping/pong 帧被uwsgi使用**。



engine.io的数据编码分为Packet和Payload，其中 Packet是数据包，有6种类型：

- 0 open：从服务端发出，标识一个新的传输方式已经打开。
- 1 close：请求关闭这条传输连接，但是它本身并不关闭这个连接。
- 2 ping：客户端周期性发送ping，服务端响应pong。注意这个与uwsgi自带的ping/pong不一样，uwsgi里面发送ping，而浏览器返回pong。
- 3 pong：服务端发送。
- 4 message：实际发送的消息。
- 5 upgrade：在转换transport前，engine.io会发送探测包测试新的transport（如websocket）是否可用，如果OK，则客户端会发送一个upgrade消息给服务端，服务端关闭老的transport然后切换到新的transport。
- 6 noop：空操作数据包，客户端收到noop消息会将之前等待暂停的轮询暂停，用于在接收到一个新的websocket强制一个新的轮询周期。

而Payload是指一系列绑定到一起的编码后的Packet，它只用在poll中，websocket里面使用websocket帧里面的Payload字段来传输数据。如果客户端不支持XHR2，则payload格式如下，其中length是数据包Packet的长度，而packet则是编码后的数据包内容(测试发现客户端发送给服务端的poll请求中的payload用的这种字符编码)。

```
<length1>:<packet1>[<length2>:<packet2>[...]]
```

若支持XHR2，则payload中内容全部以字节编码，其中第1位0表示字符串，1表示二进制数据，而后面接着的数字则是表示packet长度，然后以\xff结尾。如果一个长度为109的字符类型的数据包，则前面长度编码是 `\x00\x01\x00\x09\xff`，然后后面接packet内容。(测试发现服务端返回给客户端的payload为这种字节编码)

```
<0 for string data, 1 for binary data><Any number of numbers between 0 and 9><The number 255><packet1 (first type,
then data)>[...]
```

engine.io服务器维护了一个socket的字典结构用于管理连接到该机的客户端，而客户端的标识就是sid。**如果有多个worker，则需要保证同一个客户端的请求落在同一台worker上(可以配置nginx根据sid分发)**。因为每个worker只维护了一部分客户端连接，如果要支持广播，room等特性，则后端需要使用 redis 或者 RabbitMQ 消息队列，使用redis的话则是通过redis的订阅发布机制实现多机多worker之间的消息推送。



socket.io是engine.io的封装，在其基础上增加了自动重连，多路复用，namespace，room等特性。socket.io本身也有一套协议，它Packet类型分为`(CONNECT 0, DISCONNECT 1, EVENT 2, ACK 3, ERROR 4, BINARY_EVENT 5, BINARY_ACK 6)`。注意与engine.io的Packet类型有所不同，但是socket.io的packet实际是借助的engine.io的Message类型发送的，在后面实例中可以看到Packet的编码方式。当连接出错的时候，socket.io会通过自动重连机制重新连接。



### 4 源码分析

在建立连接后，每个客户端会被自动加入到一个默认的命名空间`/`。在每个命名空间中，socket会被默认加入两个名为`None`和`sid`的房间。None的房间用于广播，而sid是当前客户端的session id，用于单播。除默认的房间外，我们可以根据需要将对应socket加入自定义房间，roomid唯一即可。socket.io基于engine.io，支持websocket和long polling。如果是long polling，会定时发送GET, POST请求，当没有数据时，GET请求在拉取队列消息时会hang住(超时时间为pingTimeout)，如果hang住期间服务器一直没有数据产生，则需要等到客户端发送下一个POST请求时，此时服务器会往队列中存储POST请求中的消息，这样上一个GET请求才会返回。如果upgrade到了websocket连接，则探测成功之后会定期ping/pong来保活连接。流程如下图所示：



![img](https://pics3.baidu.com/feed/fcfaaf51f3deb48fcf1002b3421d3d202df57869.png?token=da8320361e3173c0fbe8eaf6d7a39150)



socketio通信流程图

为方便描述，下面提到的engine.io服务器对应源文件是`engineio/server.py`，engine.io套接字对应源文件`engineio/socket.py`，而socket.io服务器则对应`socketio/server.py`。下面分析下socket.io连接建立、消息接收和发送、连接关闭过程。socket.io版本为1.9.0，engine.io版本为2.0.4。



### 连接建立

首先，客户端会发送一个polling请求来建立连接。此时的请求参数没有sid，表示要建立连接。 engine.io服务器通过`handle_get_request()`和`handle_post_request()`方法来分别处理初始化连接以及长轮询中的 GET 和 POST 请求。



socket.io在初始化时便注册了3个事件到engine.io的handlers中，分别是`connect(处理函数_handle_eio_connect)`,`message(_handle_eio_message)`,`disconnect(_handle_eio_disconnect)`，在engine.io套接字接收到了上述三个类型的消息后，在自身做了对应处理后都会触发socket.io中的对应的处理函数做进一步处理。



当接收到GET请求且没有sid参数时，则engine.io服务器会调用 `_handle_connect()`方法来建立连接。这个方法主要工作是为当前客户端生成sid，创建Socket对象并保存到engine.io服务器的sockets集合中。做了这些初始化工作后，engine.io服务器会发送一个OPEN类型的数据包给客户端，接着会触发socket.io服务器的connect事件。



客户端第一次连接的时候，socket.io也要做一些初始化的工作，这是在socket.io服务器的`_handle_eio_connect()`处理的。这里做的事情主要有几点：

- 初始化manager，比如用的是redis做后端队列的话，则需要初始化redis_manager，包括设置redis连接配置，如果没有订阅频道则还要订阅频道`flask_socketio`(默认频道是"socket.io")，如果用到gevent，则还要对redis模块的socket库打monkey-patch等。

- 将该客户端加入到默认房间None，sid中。

- 调用代码中对connect事件注册的函数。如下面这个，注意下，socket.io中也有个用于事件处理的handlers，它保存的是在后端代码中对socket.io事件注册的函数(开发者定义的)，而engine.io的handlers中保存的函数是socket.io注册的那三个针对connect，message和disconnect事件的固定的处理函数。

  ```
  socketio.on("connect")
  def test_connect():
  print "client connected"
  ```
  
- 发送一个sockeio的connect数据包给客户端。



最后在响应中engine.io会为客户端设置一个名为io值为sid的cookie，响应内容payload包括两个数据包，一个是engine.io的OPEN数据包，内容为sid，pingTimeout等配置和参数；另一个是socket.io的connect数据包，内容为40。其中4表示的是engine.io的message消息，0则表示socket.io的connect消息，以字节流返回。这里的pingTimeout客户端和服务端共享这个配置，用于检测对端是否超时。



接着会发送一个轮询请求和websocket握手请求，如果websocket握手成功后客户端会发送`2 probe`探测帧，服务端回应`3 probe`，然后客户端会发送内容为`5`的Upgrade帧，服务端回应内容为`6`的noop帧。探测帧检查通过后，客户端停止轮询请求，将传输通道转到websocket连接，转到websocket后，接下来就开始定期(默认是25秒)的 ping/pong(**这是socket.io自定义的ping/pong，除此之外，uwsgi也会定期(默认30秒)对客户端ping，客户端回应pong，这个在chrome的Frames里面是看不到的，需要借助wireshark或者用其他浏览器插件来观察**)。



### 服务端消息接收流程

对接收消息的则统一通过engine.io套接字的`receive()`函数处理：

- 对于轮询，一旦收到了polling的POST请求，则会调用receive往该socket的消息队列里面发送消息，从而释放之前hang住的GET请求。

- 对于websocket：

- - 收到了ping，则会马上响应一个pong。
  - 接收到了upgrade消息，则马上发送一个noop消息。
  - 接收到了message，则调用socket.io注册到engine.io的`_handle_eio_message`方法来处理socket.io自己定义的各种消息。

- 因为服务端接收消息并没有用到消息队列来处理，所以要求同一个客户端的请求必须落到同一个worker上面，否则接收消息时会报`Invalid session`错误。



### 服务端消息发送流程

而服务端要给客户端发送消息，则需要通过socket.io服务器的emit方法，注意emit方法是针对room来发送消息的，如果是context-aware的，则emit默认是对namespace为/且room名为sid的房间发送，如果是context-free的，则默认是广播即对所有连接的客户端发送消息（当然在context-free的场景下面，你也可以指定room来只给指定room推送消息）。



socket.io要实现多进程以及广播，房间等功能，势必需要接入一个redis之类的消息队列，进而socket.io的emit会调用对应队列管理器pubsub_manager的emit方法，比如用redis做消息队列则最终调用 redis_manager中的_publish() 方法通过redis的订阅发布功能将消息推送到频道。另一方面，每个进程在初始化时都订阅了 频道，而且都有一个协程(或线程)在监听频道中是否有消息，一旦有消息，就会调用`pubsub_manager._handle_emit()`方法对本机对应的socket发送对应的消息，最终是通过socket.io服务器的`_emit_internal()`方法实现对本机中room为sid的所有socket发送消息的，如果room为None，则就是广播，即对所有连接到本机的所有客户端推送消息。



socket.io服务器发送消息要基于engine.io消息包装，所以归结到底还是调用的engine.io套接字中的`send()`方法。engine.io为每个客户端都会维护一个消息队列，发送数据都是先存到队列里面待拉取，websocket除了探测帧之外的其他数据帧也都是通过该消息队列发送。



### 关闭连接(只分析websocket)

websocket可能异常关闭的情况很多。比如客户端发了ping后等待pong超时关闭，服务端接收到ping跟上一个ping之间超过了pingTimeout；用的uwsgi的话，uwsgi发送ping，如果在`websockets-pong-tolerance`(默认3秒)内接收不到pong回应，也会关闭连接；还有如果nginx的proxy_read_timeout配置的比pingInterval小等。



只要不是客户端主动关闭连接，socket.io就会在连接出错后不断重试以建立连接。重试间隔和重试次数由`reconnectionDelayMax`(默认5秒)和`reconnectionAttempts`（默认一直重连）设定。下面讨论客户端正常关闭的情况，各种异常关闭情况请具体情况具体分析。



**客户端主动关闭**



假定客户端调用`socket.close()`主动关闭websocket连接，则会先发送一个消息`41`(4：engine.io的message，1：socket.io的disconnect)再关闭连接。如前面提到，engine.io套接字接收到消息后会交给socket.io服务器注册的 `_handle_eio_message()`处理。最终是调用的socket.io的`_handle_disconnect()`，该函数工作包括调用`socketio.on("disconnect")`注册的函数，将该客户端从加入的房间中移除，清理环境变量等。



uwsgi而接收到客户端关闭websocket连接消息后会关闭服务端到客户端的连接。engine.io服务器的websocket数据接收例程`ws.wait()`因为连接关闭报IOError，触发服务端循环收发数据过程停止，并从维护的sockets集合中移除这个关闭的sid。然后调用engine.io套接字的`close(wait=True, abort=True)`方法，由于是客户端主动关闭，这里就不会再给客户端发送一个CLOSE消息。而 engine.io服务器的close方法一样会触发socket.io之前注册的disconnect事件处理函数，由于前面已经调用`_handle_disconnect()`处理了关闭连接事件，所以这里`_handle_eio_disconnect()`不需要再做其他操作（这个操作不是多余的，其作用见后一节）。



**浏览器关闭**

直接关闭浏览器发送的是websocket的标准CLOSE消息，opcode为8。socket.io服务端处理方式基本一致，由于这种情况下并没有发送socket.io的关闭消息`41`，socket.io的关闭操作需要等到engine.io触发的`_handle_eio_disconnect()`中处理，这就是前一节中为什么engine.io服务器后面还要多调用一次 `_handle_eio_disconnect()`的原因所在。



### 5 实例

协议说明容易让人有点迷糊，websocket，engine.io，socket.io，各自协议是如何工作的，看看实例可能会比较清晰，为了方便测试，我写了个Dockerfile，安装了docker的童鞋可以拉取代码执行 `bin/start.sh` 即可启动拥有完整的 `nginx+uwsgi+gevent+flask_socketio`测试环境的容器开始测试，浏览器打开`http://127.0.0.1`即可测试。flask_socketio支持的异步模式有threading, eventlet, gevent 和 gevent_uwsgi等，我的测试环境async_mode用的是`gevent_uwsgi`，完整代码见 这里。



对于不支持websocket的低版本浏览器，socket.io会退化为长轮询的方式，通过定期的发送GET, POST请求来拉取数据。没有数据时，会将请求数据的GET请求hang住，直到服务端有数据产生或者客户端的POST请求将GET请求释放，释放之后会紧接着再次发送一个GET请求，除此之外，数据编解码和处理流程与websocket方式基本一致。实例只针对websocket进行分析，如果要测试长轮询，可以将nginx配置中的proxy_set_header中的Connection和Upgrade去掉即可。



为了观察socket.io客户端的调用流程，可以设置`localStorage.debug = '*';`，测试的前端代码片段如下(完整代码见仓库)：

```
<script type="text/javascript" charset="utf-8">
var socket = io.connect('/', {
"reconnectionDelayMax": 10000,
"reconnectionAttempts": 10
});
socket.on('connect', function() {
$('#log').append('<br>' + $('<div/>').text('connected').html());
})

$(document).ready(function() {

socket.on('server_response', function(msg) {
$('#log').append('<br>' + $('<div/>').text('Received from server: ' + ': ' + msg.data).html());
});

$('form#emit').submit(function(event) {
socket.emit('client_event', {data: $('#emit_data').val()});
return false;
});
});

</script>
```



测试代码比较简单，引入socket.io的js库文件，然后在连接成功后在页面显示“connected”，在输入框输入文字，可以通过连接发送至服务器，然后服务器将浏览器发送的字符串加上server标识回显回来。



### 建立连接

在chrome中打开页面可以看到发了3个请求，分别是：

```
1 http://127.0.0.1/socket.io/?EIO=3&transport=polling&t=MAkXxBR
2 http://127.0.0.1/socket.io/? EIO=3&transport=polling&t=MAkXxEz&sid=9c54f9c1759c4dbab8f3ce20c1fe43a4
3 ws://127.0.0.1/socket.io/?EIO=3&transport=websocket&sid=9c54f9c1759c4dbab8f3ce20c1fe43a4
```

请求默认路径是`/socket.io`，注意命名空间并不会在路径中，而是在参数中传递。第1个请求是polling，EIO是engine.io协议的版本号，t是一个随机字符串，第一个请求时还还没有生成sid。服务端接收到消息后会调用`engine.io/server.py`的`_handle_connect()`建立连接。

返回的结果是

```
## Response Headers: Content-Type: application/octet-stream ##
0{"pingInterval":25000,"pingTimeout":60000,"upgrades":["websocket"],"sid":"9c54f9c1759c4dbab8f3ce20c1fe43a4"}40
```

可以看到，这里返回的是字节流的payload，content-type为"application/octet-stream"。这个payload其实包含两个packet，第一个packet是engine.io的OPEN消息，类型为0，它的内容为pingInterval，pingTimeout，sid等；第二个packet类型是4(message)，而它的数据内容是0，表示socket.io的CONNECT。而其中的看起来乱码的部分实则是前面提到的payload编码中的长度的编码`\x00\x01\x00\x09\xff`和`\x00\x02\xff`。



如果在js代码中将io.connect的namespace参数不用默认的`/`，而设置为`/demo`，那么连接时还会发一个POST请求带上`7:40/demo`的字符格式payload(其中7是数据长度，4是engineio的message，0则是表示socket.io的connect类型消息)，服务器接收到该POST请求后会将该客户端再加入到`/demo`命名空间中。

- 第2个请求是轮询请求，如果websocket建立并测试成功(使用内容为probe的ping/pong帧)后，会暂停轮询请求。可以看到轮询请求一直hang住到websocket建立并测试成功后才返回，响应结果是`6`，前面乱码部分是payload长度编码`\x00\x01\xff`，后面的数字6是engine.io的noop消息。

- 第3个请求是websocket握手请求，握手成功后，可以在chrome的`Frames`里面看到websocket的数据帧交互流程，可以看到如前面分析，确实是先发的探测帧，然后是Upgrade帧，接着就是定期的`ping/pong`帧了。

  ```
  2probe
  3probe
  5
  2
  3
  ...
  ```



### 客户端发送消息给服务端

如果要发送消息给服务器，在浏览器输入框输入`test`，点击echo按钮，可以看到websocket发送的帧的内容如下，其中4是engine.io的message类型标识，2是socket.io的EVENT类型标识，而后面则是事件名称和数据，数据可以是字符串，字典，列表等类型。

```
42["client_event",{"data":"test"}]
```



### 服务端接收消息流程

而服务端接收消息并返回一个新的event为"server_response"，数据为"TEST"，代码如下，其中socketio是flask_socketio模块的SocketIO对象，它提供了装饰器方法 on将自定义的client_event和处理函数test_client_event注册到sockerio服务器的handlers中。



当接收到 client_event 消息时，会通过`sockerio/server.py`中的 `_handle_eio_message()`方法处理消息，对于socket.io的EVENT类型的消息最终会通过`_trigger_event()`方法处理，该方法也就是从handlers中拿到client_event对应的处理函数并调用之。

```
from flask_socketio import SocketIO, emit
socketio = SocketIO(...)

@socketio.on("client_event")
def test_client_event(msg):
emit("server_response", {"data": msg["data"].upper()})
```



### 服务端发送消息到客户端

服务端发送消息通过 flask_socketio提供的emit方法实现，如前一节分析的，最终还是通过的engine.io包装成engine.io的消息格式后发出。

```
42["server_response",{"data":"TEST"}]
```



### 关闭连接

客户端要主动关闭连接，在JS中调用 `socket.close()` 即可，此时发送的数据包为 `41`，其中4代表的是engine.io的消息类型message，而数据1则是指的socket.io的消息类型disconnect，关闭流程见上一章的说明。



### 几个小点

假如客户端连接时namespace为`/demo`，而服务端发送消息`emit(namespace="/")`指定的命名空间为默认的`/`，那这个消息是否会发给客户端？答案是会。因为前面说到，每个客户端默认加入到了`/`中，所以，服务端的消息肯定会发给客户端的，但是客户端接收到消息会检查namespace是否与其connect时的namespace一致，如果不一致，虽然接收到了消息但是并不会触发客户端的操作。



如果客户端想知道自己发送的事件是否被服务端成功接收，可以在emit里面加回调函数，如下所示。加了回调函数后客户端发送的消息格式为`421["client_event",{"data":"test"}]`，即在原来基础上多加了一个id标识1，服务端接收到事件后，发现消息中有id，则会多发送一个socket.io的ACK包给客户端，内容为该事件处理函数的返回值，客户端收到ACK包后会调用下面的callback。

```
socket.emit('client_event', {data: $('#message').val()}, callback);
```

而服务端如果要确认发送的消息是否被客户端接收到，可以在emit函数里面指定 callback参数，而客户端的事件监听里面回调函数加多一个ack参数并调用ack函数即可，这样客户端收到了服务端的消息后，调用ack时就会发送一个ACK消息给服务端，ack函数里面也可以传参数给服务端。

```
### 服务端
flask_socketio.emit("server_response", {"data": "xxx"}, callback=callback)

### 客户端
socket.on('server_response', function(msg, ack) {
...
ack();
});
```



### 6 总结

本文示例中，为了便于分析，只用了默认的namespace和room，而在项目中可以根据业务需要使用namespace，room等高级特性。在`nginx+uwsgi`使用socket.io时，注意nginx的超时配置proxy_read_timeout和uwsgi的websocket超时配置websocket-ping-freq和websockets-pong-tolerance，配置不当会导致socke.io因为websocket的ping/pong超时而不断重连。如果要禁用websocket，可以在SocketIO参数里面加上`allow_upgrades=False`即可。



调研了一些其他系统WEB端的推送机制，微信网页版没有用websocket，而是统一用的长轮询的方式。今日头条WEB版其实都没有实时推送信息流，而是定时提示用户去手动点击刷新。即刻WEB版则是用的短连接定期拉取是否有未读消息，不过它也用到了socket.io。