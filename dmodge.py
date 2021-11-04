from discord.ext import commands

from dmoj_client import DmojClient


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

    @commands.command()
    async def get_user_submission(self, ctx, user, problem_id = None):
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
    async def create_contest(self, ctx, contest_name, *problems):
        if len(problems) == 0:
            await ctx.send("A list of problem(s) is required to create a contest")
            return

        await ctx.send("Received create contest command")


