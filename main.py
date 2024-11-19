# 主函数：建立 WebSocket 连接并订阅交易日志
async def main():
    threading.Thread(target=enqueue_transactions_every_two_seconds, daemon=True).start()

    httpRPC_list = ReadHTTPRPC()
    SOLANA_HTTP_URL = random.choice(httpRPC_list)

    # 动态创建和释放线程来处理交易队列中的任务
    threading.Thread(target=worker, args=(SOLANA_HTTP_URL,), daemon=True).start()

    # 北京时间时区
    beijing_timezone = pytz.timezone("Asia/Shanghai")

    while True:
        # 获取当前时间（北京时区）
        now = datetime.now(beijing_timezone).time()

        # 设置允许的交易时间段
        # 创建配置解析器
        config = configparser.ConfigParser()
        config.read(os.path.abspath('config.ini'))
        start_time_limit = str(config['DEFAULT']['start_time_limit'])
        end_time_limit = str(config['DEFAULT']['end_time_limit'])

        start_time = datetime.strptime(f"{start_time_limit}:00", "%H:%M").time()
        end_time = datetime.strptime(f"{end_time_limit}:00", "%H:%M").time()

        # 检查当前时间是否在允许的交易时间段内
        if start_time <= now or now <= end_time:
            print("当前时间在允许的交易时间段内，启动 WebSocket 连接")
            wss_pumpfun = "wss://frontend-api.pump.fun/socket.io/?EIO=4&transport=websocket"
            try:
                async with websockets.connect(wss_pumpfun) as websocket:
                    print("Connected to WebSocket")
                    # 发送一个初始的ping消息，适用于部分WebSocket服务器要求的验证或心跳信息
                    await websocket.send("40")  # 发送初始的握手信息
                    print("Initial handshake sent")
                    await listen_for_logs(websocket, wss_pumpfun)
            except Exception as e:
                traceback.print_exc()  # 打印完整的错误堆栈信息
                print(f"WebSocket 连接出错: {e}")
        else:
            # 如果不在允许时间段内，则暂停执行
            print("当前时间不在允许的交易时间段内，程序暂停执行")
            time.sleep(60)  # 每隔 5 分钟检查一次时间

# 启动程序
if __name__ == "__main__":
    asyncio.run(main())
