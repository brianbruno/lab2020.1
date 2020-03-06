import requests
import time
from json import dump
from json import loads

def run_query(json, headers): # A simple function to use requests.post to make the API call. 

    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))

query = """
{
  search(query:"stars:>100", type:REPOSITORY, first:10 {AFTER}){
    pageInfo{
        hasNextPage
        endCursor
    }
    nodes{
      ... on Repository
      {
        nameWithOwner
        url
        createdAt
        updatedAt
        primaryLanguage {
          id
          name
        }
        pullRequests{
          totalCount
        }
        acceptedsPullRequests: pullRequests(states:MERGED)
        {
          totalCount
        }
        releases
        {
          totalCount
        }
        closedIssues: issues(states:CLOSED)
        {
          totalCount
        }
        totalIssues: issues
        {
          totalCount
        }
      }
    }
    pageInfo
    {
      endCursor
    }
  }
}
"""

finalQuery = query.replace("{AFTER}", "")

json = {
    "query":finalQuery, "variables":{}
}

token = 'b86bb92aa54dcef4d2b470ecf46ee6a01ac3dc7d' #insert your token
headers = {"Authorization": "Bearer " + token} 

total_pages = 1

result = run_query(json, headers)
nodes = result['data']['search']['nodes']
next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]

#paginating
while (next_page and total_pages < 100):
    try:

      print("Paginas: "+str(total_pages))
      time.sleep(30)
      total_pages += 1
      cursor = result["data"]["search"]["pageInfo"]["endCursor"]
      next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
      json["query"] = next_query
      result = run_query(json, headers)
      # nodes += result['data']['search']['nodes']
      next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]

      #saving data
      for node in result['data']['search']['nodes']:
        if (node['primaryLanguage'] is None):
          primaryLanguage  = 'None'
        else:
          primaryLanguage  = node['primaryLanguage']['name']

        with open("repos.csv", 'a') as the_file:
          the_file.write(node['nameWithOwner'] + "," + 
            node['createdAt'] + "," + 
            node['updatedAt'] + "," + 
            str(node['acceptedsPullRequests']['totalCount']) + "," + 
            str(node['releases']['totalCount']) + "," +
            str(node['closedIssues']['totalCount']) + "," + 
            str(node['totalIssues']['totalCount']) + "\n") 
    except:
      print('Tentando novamente')
      time.sleep(60)
