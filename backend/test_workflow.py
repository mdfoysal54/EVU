from app.workflow import (
    EdgeSpec,
    NodeSpec,
    WorkflowDefinition,
    WorkflowExecutor,
)


def start(context):
    context.set("number", 10)

    return 10


def double(context):
    value = context.get("number", 0)

    value *= 2

    context.set("number", value)

    return value


def finish(context):
    value = context.get("number", 0)

    context.set(
        "final",
        value,
    )

    return value


workflow = WorkflowDefinition(
    id="example-workflow",
    name="Example Workflow",
    nodes=[
        NodeSpec(
            id="start",
            name="Start",
            handler=start,
        ),
        NodeSpec(
            id="double",
            name="Double",
            handler=double,
        ),
        NodeSpec(
            id="finish",
            name="Finish",
            handler=finish,
        ),
    ],
    edges=[
        EdgeSpec(
            source="start",
            target="double",
        ),
        EdgeSpec(
            source="double",
            target="finish",
        ),
    ],
)


executor = WorkflowExecutor()

result = executor.execute_sync(
    workflow
)

print("SUCCESS:", result.success)
print("ERROR:", result.error)
print(
    "VARIABLES:",
    result.state.variables,
)