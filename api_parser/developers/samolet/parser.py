import requests

session = requests.Session()


session.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Cookie': 'csrftoken=hV5vvqshAnNCiCiwZQwX2t6dMWsSmQvx; suggested_city=1; _smt=5aded1f1-eed9-428e-add9-e5fe5d4daab5; _pk_id.63560702.50e9=ede7280667c6603e.1716036192.; __exponea_etc__=8db03ded-0a5d-4f61-8b8c-e181cf775d1e; _ct=1300000000423474344; _ct_client_global_id=297e3204-78dd-5347-b21e-06186857efc4; _ym_uid=1716036196868235914; _ym_d=1716036196; _ga=GA1.1.636443152.1716036196; FPID=FPID2.2.CR8xjNz6TV7LUgaS8QAfpetGBbkcsqKUlVVnQ40s6qY%3D.1716036196; tmr_lvid=e84502a629192ec9de1a2245b1fe9200; tmr_lvidTS=1716036196404; _ga_2WZB3B8QT0=GS1.1.1716038846.2.0.1716038846.0.0.870437590; qrator_jsr=1741020630.362.vbEsSMe6FI45iNVl-n0qphovcsccb70jcr5kfrbo26voerkk8-00; qrator_jsid=1741020630.362.vbEsSMe6FI45iNVl-g9oc8luinjr5nj8rru0f53tcnuekdp6m'
}


projects = session.get(
    url='https://samolet.ru/project/',

)


print(projects.content)