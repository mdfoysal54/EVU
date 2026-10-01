import asyncio

from app.coding import (
    CodingAgent,
    Workspace,
)

from app.experience import (
    ExperienceService,
)


async def main():

    workspace = Workspace.create(
        root="./evu_test_workspace"
    )

    workspace.write(
        "hello.py",
        """
def hello():
    return "Hello EVU"


if __name__ == "__main__":
    print(hello())
""".strip()
        + "\n",
    )

    experience = ExperienceService()

    agent = CodingAgent(
        workspace,
        experience_service=experience,
    )

    result = await agent.execute(
        "Inspect the project and verify the Python code.",
        run_tests=False,
        required_files=[
            "hello.py"
        ],
    )

    print(
        "Success:",
        result.success,
    )

    print(
        "Plan:",
        result.plan,
    )

    print(
        "Verification:",
        result.verification,
    )

    print(
        "Experiences:",
        experience.collector.count(),
    )


asyncio.run(main())