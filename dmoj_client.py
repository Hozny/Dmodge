import requests

class DmojClient():
    async def get_user_submission_raw(self, user, problem_id = None):
        url_endpoint = "https://dmoj.ca/api/v2/submissions"
        params = {"user": user, "problem": problem_id}

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

    async def get_problem(self, id):
        url_endpoint = f"https://dmoj.ca/api/v2/problem/{id}"
        resp = requests.get(url_endpoint)
        try:
            resp_data = resp.json()["data"]["object"]
        except KeyError:
            return None
        
        return resp_data

    async def is_user_exist(self, user_id):
        url_endpoint = f"https://dmoj.ca/api/v2/user/{user_id}"
        resp = requests.get(url_endpoint)
        resp_data = resp.json()

        return False if "error" in resp_data else True;

    async def get_user_submissions(self, user_id, problem_id):
        """
        :returns: (bool, int) bool for if problem was solved 
                  int for number of non-AC submissions before first AC
                  None if failed query
        """
        if not await self.is_user_exist(user_id):
            return None, None

        url_endpoint = f"https://dmoj.ca/api/v2/submissions"
        params = {"user": user_id, "problem": problem_id}
        resp = requests.get(url_endpoint, params)
        try:
            resp_data = resp.json()["data"]["objects"]
        except KeyError:
            return None, None
        '''
        if len(resp_data) == 0:
            return None, None
        '''
        wrong = 0
        accepted = False
        for submission in resp_data:
            if submission["result"] == "AC":
                accepted = True
                break
            wrong += 1
        return accepted, wrong
