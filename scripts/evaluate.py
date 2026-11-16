import argparse,json,os,time,urllib.request
CASES=[
 {"question":"What is the expense reimbursement limit?","expected_terms":["reimbursement","expense"]},
 {"question":"How many tickets were resolved by team?","expected_terms":["team","tickets"]},
 {"question":"What is the escalation process?","expected_terms":["escalation"]},
]
def main():
 p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://localhost:8000');p.add_argument('--api-key',default=os.getenv('API_KEY',''));a=p.parse_args();results=[]
 for c in CASES:
  body=json.dumps({"question":c['question'],"mode":"auto"}).encode();req=urllib.request.Request(a.base_url+'/v1/chat',data=body,headers={'Content-Type':'application/json','X-API-Key':a.api_key})
  start=time.perf_counter()
  try:
   with urllib.request.urlopen(req,timeout=90) as r: data=json.loads(r.read())
   elapsed=(time.perf_counter()-start)*1000; answer=data['answer'].lower(); hit=sum(t in answer for t in c['expected_terms'])/len(c['expected_terms'])
   results.append({"question":c['question'],"latency_ms":round(elapsed,2),"term_coverage_proxy":round(hit,2),"has_sources":bool(data.get('sources')),"request_metrics":data.get('metrics',{})})
  except Exception as e: results.append({"question":c['question'],"error":str(e)})
 os.makedirs('artifacts',exist_ok=True);out={"warning":"Term coverage is a simple proxy, not a validated factuality metric.","results":results};open('artifacts/evaluation.json','w').write(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
