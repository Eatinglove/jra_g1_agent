# jra_g1_agent
use this agent to answer some simple problem about race history

首先執行crawl.py他會上jra的網站爬下歷年(1970年以後)的各G1比賽的結果，存在一個資料夾裡面，每個比賽就會有一個.txt

然後執行save.py，他會把爬下來的資料進行處理，儲存成db.json檔案，方便之後使用

最後執行llm.py，在這裡就可以問問題了

又或者直接下載db.json，裡面已經處理過了，這樣就不用執行crawl.py跟save.py了

missing_data.txt代表沒有資料的比賽
