[33mcommit 801ad1801b3645c0aaba0033c787179175d33508[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Merge: 88c8a70 efbe30f
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Fri Dec 12 13:34:45 2025 +0530

    Merge branch 'main' of https://github.com/ItsHiteshKr/stock_backend

[33mcommit 88c8a70fca2cd9e7682f9dd48c43e8dd54ff4843[m
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Fri Dec 12 13:33:23 2025 +0530

    Added stock comparision apis and endpoints for listing and searching stocks and indices

 main.py                        |   8 [32m+++[m
 model/daily_data.py            |   1 [32m+[m
 model/index.py                 |   8 [32m+++[m
 model/stock.py                 |   8 [32m+++[m
 router/comparison_routes.py    |  42 [32m++++++++++++++++[m
 router/index_router_for_UI.py  |  48 [32m++++++++++++++++++[m
 router/stocks_router_for_UI.py |  52 [32m+++++++++++++++++++[m
 schema/index_schema_UI.py      |  17 [32m+++++++[m
 schema/stock_schema_UI.py      |  12 [32m+++++[m
 service/comparison_service.py  | 111 [32m+++++++++++++++++++++++++++++++++++++++++[m
 service/historical_fetch.py    |  73 [32m++++++++++++++++++++++[m[31m-----[m
 service/populate_stocks.py     |  92 [32m++++++++++++++++++++++++++++++++++[m
 12 files changed, 460 insertions(+), 12 deletions(-)

[33mcommit efbe30f79c88422ce0f9490c756d00e6e36e9afa[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Thu Dec 11 17:27:02 2025 +0530

    Added debug On Off Button via .env Files

 main.py | 9 [32m+++++++[m[31m--[m
 1 file changed, 7 insertions(+), 2 deletions(-)

[33mcommit 114d50558a872f88fa4edaef9bab996c6d548b71[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Thu Dec 11 16:29:01 2025 +0530

    Correct whislist route &add list whislist name

 router/watchlist_router.py   | 25 [32m+++++++++++++++[m[31m----------[m
 schema/watchlist_schema.py   |  6 [32m+++++[m[31m-[m
 service/watchlist_service.py | 15 [32m+++++++++++++[m[31m--[m
 3 files changed, 33 insertions(+), 13 deletions(-)

[33mcommit 52c2b49e77b6dc9eea3e55ffb36af9a6c26021dd[m
Merge: 62d3149 c639d74
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Wed Dec 10 16:03:08 2025 +0530

    Merge branch 'main' of https://github.com/ItsHiteshKr/stock_backend

[33mcommit 62d3149ab0afaf4922942f0a06b02473e99ecdc1[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Wed Dec 10 16:01:20 2025 +0530

    Correct whislist route for showing symbol count

 schema/watchlist_schema.py   |  8 [32m++++++[m[31m--[m
 service/watchlist_service.py | 13 [32m++++++++[m[31m-----[m
 2 files changed, 14 insertions(+), 7 deletions(-)

[33mcommit c639d74b66e6e1d3be3021853598a3f9be7d4137[m
Merge: 4f2fe24 7e0fae6
Author: Yukti Chaurasia <166976936+yukti2911@users.noreply.github.com>
Date:   Wed Dec 10 15:58:36 2025 +0530

    Merge pull request #5 from ItsHiteshKr/ind_api
    
    Added the technical indicator apis and updated the live_stock api

[33mcommit 7e0fae6c4eb791d0c523c89eb63ccbc7820f0844[m
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Wed Dec 10 15:56:42 2025 +0530

    Added the technical indicator apis and updated the live_stock api

 main.py                       |   2 [32m+[m
 requirements.txt              |   2 [32m+[m
 router/indicators_router.py   |  79 [32m++++++++++++++++++++++++++++++[m
 schema/live_stock_schema.py   |   7 [32m+++[m
 service/analysis_service.py   | 111 [32m++++++++++++++++++++++++++++++++++++++++++[m
 service/live_stock_service.py |  44 [32m+++++++++++++++[m[31m--[m
 6 files changed, 240 insertions(+), 5 deletions(-)

[33mcommit 4f2fe24ea219f86be7d082fdaf969ca847c89b21[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Tue Dec 9 13:51:26 2025 +0530

     remove company name from the watchlist  symbol

 router/watchlist_router.py   | 6 [32m+++[m[31m---[m
 service/watchlist_service.py | 5 [32m+++++[m
 2 files changed, 8 insertions(+), 3 deletions(-)

[33mcommit 6b71b5fc5122ea421b122705c2b31ee54106f8f1[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Tue Dec 9 02:51:03 2025 +0530

    user can add more than 1  watchlist with route

 db/database.py               |  14 [32m++[m[31m--[m
 main.py                      |  11 [32m++[m[31m-[m
 model/watchlist_model.py     |  10 [32m+++[m
 router/watchlist_router.py   |  65 [32m+++++++++++++++++[m
 schema/watchlist_schema.py   |  20 [32m+++++[m
 service/watchlist_service.py | 170 [32m+++++++++++++++++++++++++++++++++++++++++++[m
 6 files changed, 280 insertions(+), 10 deletions(-)

[33mcommit cd972db5480b4165d1849111719dde41aaaf853b[m
Merge: d9f9277 8eb4fd4
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Mon Dec 8 23:21:16 2025 +0530

    Merge branch 'main' of https://github.com/ItsHiteshKr/stock_backend

[33mcommit d9f9277a5ed5928a3bbcc79df6b725285c675493[m
Merge: 705c081 03a2506
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Mon Dec 8 23:21:11 2025 +0530

    pull

[33mcommit 8eb4fd49e11c60390e73c2c1c9d4217e620b3b6d[m
Merge: 03a2506 0275612
Author: Yukti Chaurasia <166976936+yukti2911@users.noreply.github.com>
Date:   Mon Dec 8 10:13:08 2025 +0530

    Merge pull request #4 from ItsHiteshKr/hist_api
    
    Add the APIs for Monthly & Historical Analysis

[33mcommit 0275612eb96a591fc8f100059744e6231033c038[m
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Fri Dec 5 13:59:33 2025 +0530

    Add the APIs for Monthly & Historical Analysis

 main.py                     |  12 [32m+++[m[31m-[m
 model/daily_data.py         |  16 [32m+++++[m
 router/analysis_router.py   |  28 [32m+++++++++[m
 schema/analysis_schema.py   |  24 [32m++++++++[m
 service/analysis_service.py | 142 [32m++++++++++++++++++++++++++++++++++++++++++++[m
 service/daily_updater.py    |  68 [32m+++++++++++++++++++++[m
 service/historical_fetch.py |  42 [32m+++++++++++++[m
 7 files changed, 330 insertions(+), 2 deletions(-)

[33mcommit 705c0815e53f88b2b0db010ce2c42868022a660b[m
Author: ItsHiteshKr <simasinhabih1@gmail.com>
Date:   Thu Dec 4 17:57:30 2025 +0530

    pull

 service/live_stock_service.py | 3 [32m++[m[31m-[m
 1 file changed, 2 insertions(+), 1 deletion(-)

[33mcommit 03a2506e70ece72cfa3105ce01b966a045d9b01e[m
Merge: 2296698 f0d2f57
Author: vashu mogha <vashumogha13@gmail.com>
Date:   Thu Dec 4 17:54:10 2025 +0530

    Resolve merge conflicts: README.md (and main.py if applicable)

[33mcommit 2296698a3702cd68013a649f09121aef6737ee00[m
Merge: c665469 0fda514
Author: vashu mogha <vashumogha13@gmail.com>
Date:   Thu Dec 4 17:50:46 2025 +0530

    pull

[33mcommit f0d2f57b9bb286c65d96b82c8db2c58e46d4231c[m
Merge: 03759bc 83d2453
Author: Yukti Chaurasia <166976936+yukti2911@users.noreply.github.com>
Date:   Thu Dec 4 14:14:01 2025 +0530

    Merge pull request #3 from ItsHiteshKr/live_api
    
    Update live stock API to use yfinance instead of NSE

[33mcommit 83d2453021bbbf5fff531caa8e01eb69382c10c2[m
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Thu Dec 4 14:07:42 2025 +0530

    Update live stock API to use yfinance instead of NSE

 router/live_stock_router.py   | 10 [32m+++[m[31m-------[m
 service/live_stock_service.py | 45 [32m+++++++++++[m[31m--------------------------------[m
 2 files changed, 14 insertions(+), 41 deletions(-)

[33mcommit 03759bc16ced11ed6b9cef1328efda058c4e27e3[m
Merge: 0fda514 c4941a3
Author: Yukti Chaurasia <166976936+yukti2911@users.noreply.github.com>
Date:   Thu Dec 4 13:13:09 2025 +0530

    Merge pull request #2 from ItsHiteshKr/api_2
    
    Added Stock Screener APIs

[33mcommit c66546974452e2a8b15ed73e9dc92c13f685c753[m
Author: vashu mogha <vashumogha13@gmail.com>
Date:   Thu Dec 4 11:57:31 2025 +0530

    pull

 service/live_stock_service.py | 2 [32m+[m[31m-[m
 1 file changed, 1 insertion(+), 1 deletion(-)

[33mcommit c4941a346ad5f5d3980b0fbe2edc257289db0f83[m
Author: Yukti Chaurasia <chaurasiayukti29@gmail.com>
Date:   Thu Dec 4 11:45:13 2025 +0530

    Added instructions for fundamentals update command

 README.md | 22 [32m++++