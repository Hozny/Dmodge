import requests

class DmojClient():
    async def get_user_submission(self, user, problem_id = None):
        url_endpoint = "https://dmoj.ca/api/v2/submissions"
        params = {"user": user, "problem": problem_id}
        if problem_id is not None:
            params["problem"] = problem_id

        resp = requests.get(url_endpoint, params=params)
        resp_data = resp.json()["data"]["objects"]

        return resp_data
    
    async def search_problems(self, query):
        """
        :returns: list of (example): 
        {
            "code": "cco03p1", 
            "name": "CCO '03 P1 - BFed",
            "types": ["Uncategorized"],
            "group": "CCO", 
            "points": 10.0,
            "partial": false,
            "is_organization_private": false,
            "is_public": true
        }
        """
        url_endpoint = "https://dmoj.ca/api/v2/problems"
        params = {"search": query}

        resp = requests.get(url_endpoint, params=params)
        resp_data = resp.json()["data"]["objects"]
        
        return resp_data
    





