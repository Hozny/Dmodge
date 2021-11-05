import shelve
from discord.ext import commands

from dmoj_client import DmojClient


class DB():
    def __init__(self, file_name):
        self._file_name = file_name

    def get(self, key):
        with shelve.open(self._file_name, 'c') as shelf:
            if key in shelf:
                return shelf[key]
        return None
    
    def set(self, key, value):
        with shelve.open(self._file_name, 'c') as shelf:
            shelf[key] = value

    def all(self):
        """
        :returns: read-only copy of DB, writes to this will not persist
        """
        with shelve.open(self._file_name, 'c') as shelf:
            return dict(shelf)

'''
data to save
    - save user -> dmoj id
    - save contest -> discord user:dmoj id, problems_list
commands
    - check user solved problem
    - create contest
        - contest name, problems
    - get contest result
        - save user results -> csv
    - end contest
        - run get contest
'''
class Dmodge(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._dmoj_client = DmojClient()

        self._users_db = DB("users")

    @commands.command()
    async def get_user_submissions(self, ctx, user, problem_id = None):
        """
        !get_user_submission user [problem_id]
        """
        print("received command")
        submissions = await self._dmoj_client.get_user_submission(user, problem_id)
        await ctx.send("I truncated response to :" + str(submissions)[:1000])

    @commands.command()
    async def search_problems(self, ctx, query):
        problems = await self._dmoj_client.search_problems(query)

        num_problems = 4
        resp = f"The top {num_problems} problems matching are:\n"
        for i, problem in enumerate(problems):
            if i >= num_problems: break

            name = problem["name"]
            code = problem["code"]
            problem_str = f"Name: {name} - problem_code: {code}\n"
            resp = resp + problem_str

        await ctx.send(resp)

    @commands.command()
    async def create_contest(self, ctx, contest_name, *problem_links):
        if len(problem_links) == 0:
            await ctx.send("A list of problem(s) is required to create a contest")
            return

        ret = f"Creating contest: {contest_name} with problems:\n"
        for i, problem_url in enumerate(problem_links):
            problem_id = self._get_problem_id_from_url(problem_url)
            problem = await self._dmoj_client.get_problem(problem_id)
            name = problem["name"]
            points = problem["points"]

            ret = ret + f"{i+1}: problem_id= {problem_id}, name={name}, points={points}\n"

        await ctx.send(ret)
    
    @commands.command()
    async def link_dmoj_account(self, ctx, user_id):
        if not await self._dmoj_client.is_user_exist(user_id):
            await ctx.send(f"Could not find DMOJ user matching name: {user_id}")
            return

        author = ctx.author.name
        user_data = self._users_db.all()
        if user_data.get(author) == user_id:
            await ctx.send(f"You're already linked to this account")
            return
        if user_id in user_data.values():
            await ctx.send(f"Account already linked to someone; ask them to unlink or ask for help")
            return

        self._users_db.set(author, user_id)
        await ctx.send(f"Succesfully linked accounts discord: {author} to dmoj: {user_id}")

    def _get_problem_id_from_url(self, str):
        i = str.rfind("/")
        ret = str[i+1:] if i + 1 < len(str) and i != -1 else str
        return  ret

