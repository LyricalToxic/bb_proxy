import typing as t

import click


class Password(click.ParamType):
    name = "password"
    MIN_LENGTH = 4
    MAX_LENGTH = 20

    def convert(
            self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
    ) -> t.Any:
        if not isinstance(value, str):
            self.fail(f"Password must be a {type(str)}, but got {type(value)}", param, ctx)
        else:
            if not self.MIN_LENGTH <= len(value) <= self.MAX_LENGTH:
                self.fail(
                    f"Password ({value}) length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH}", param, ctx,
                )
        return value
