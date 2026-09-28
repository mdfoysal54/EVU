from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import List


@dataclass
class RouteInfo:
    path: str
    method: str

    function: str
    file: str

    line: int

    framework: str = "unknown"

    metadata: dict = field(
        default_factory=dict
    )


class RouteDetector:
    """
    Detects common Python web routes from source AST.

    Supported patterns include:
      @app.get("/users")
      @app.post("/users")
      @router.get("/users")
      @router.post("/users")
    """

    HTTP_METHODS = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "options",
        "head",
    }

    def detect(
        self,
        source: str,
        file: str = "",
    ) -> List[RouteInfo]:
        tree = ast.parse(
            source,
            filename=file or "<source>",
        )

        routes: list[RouteInfo] = []

        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            for decorator in node.decorator_list:
                route = self._parse_decorator(
                    decorator
                )

                if route is None:
                    continue

                method, path, framework = route

                routes.append(
                    RouteInfo(
                        path=path,
                        method=method.upper(),
                        function=node.name,
                        file=file,
                        line=getattr(
                            node,
                            "lineno",
                            0,
                        ),
                        framework=framework,
                    )
                )

        return routes

    def _parse_decorator(
        self,
        decorator: ast.AST,
    ):
        if not isinstance(
            decorator,
            ast.Call,
        ):
            return None

        function = decorator.func

        if not isinstance(
            function,
            ast.Attribute,
        ):
            return None

        method = function.attr.lower()

        if method not in self.HTTP_METHODS:
            return None

        if not decorator.args:
            return None

        first = decorator.args[0]

        if not isinstance(
            first,
            ast.Constant,
        ):
            return None

        if not isinstance(
            first.value,
            str,
        ):
            return None

        framework = "fastapi"

        if isinstance(
            function.value,
            ast.Name,
        ):
            object_name = function.value.id

            if object_name == "app":
                framework = "fastapi"
            elif object_name == "router":
                framework = "router"

        return (
            method,
            first.value,
            framework,
        )