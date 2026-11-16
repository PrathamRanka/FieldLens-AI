import argparse,json,os,time,statistics,urllib.request,concurrent.futures

def main():
 p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://localhost:8000');p.add_argument('--api-key',default=os.getenv('API_KEY',''));p.add_argument('--requests',type=int,default=30);a=p.parse_args()
 def one(i):
  body=json.dumps({"question":"Summarise the available operational metrics by team.","mode":"analytics"}).encode();req=urllib.request.Request(a.base_url+'/v1/chat',data=body,headers={'Content-Type':'application/json','X-API-Key':a.api_key});t=time.perf_counter()
  try:
   with urllib.request.urlopen(req,timeout=120) as r: r.read()
   return (time.perf_counter()-t)*1000,None
  except Exception as e:return None,str(e)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: rows=list(ex.map(one,range(a.requests)))
 vals=[x[0] for x in rows if x[0] is not None];out={"requests":a.requests,"successes":len(vals),"failures":a.requests-len(vals),"p50_ms":round(statistics.median(vals),2) if vals else None,"p95_ms":round(sorted(vals)[max(0,int(len(vals)*.95)-1)],2) if vals else None,"warning":"Run against a controlled deployment. These are observed client-side latencies, not a service-level guarantee."}
 os.makedirs('artifacts',exist_ok=True);open('artifacts/benchmark.json','w').write(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
