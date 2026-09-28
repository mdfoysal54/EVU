from app.pipeline import (
    FunctionStage,
    Pipeline,
    PipelineContext,
    PipelineRunner,
)


def add_input(context: PipelineContext):
    context.set("number", 10)
    return 10


def double_input(context: PipelineContext):
    value = context.get("number", 0)
    value *= 2

    context.set("number", value)

    return value


def final_output(context: PipelineContext):
    value = context.get("number", 0)

    context.set("output", value)

    return value


pipeline = Pipeline(
    name="example_pipeline"
)

pipeline.add_stage(
    FunctionStage(
        name="add_input",
        function=add_input,
    )
)

pipeline.add_stage(
    FunctionStage(
        name="double_input",
        function=double_input,
    )
)

pipeline.add_stage(
    FunctionStage(
        name="final_output",
        function=final_output,
    )
)


runner = PipelineRunner()

result = runner.run(
    pipeline
)

print("SUCCESS:", result.success)
print("OUTPUT:", result.output)
print(
    "COMPLETED:",
    result.completed_stages,
)
print(
    "ERROR:",
    result.error,
)