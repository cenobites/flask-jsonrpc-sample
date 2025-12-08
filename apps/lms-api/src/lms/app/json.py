import typing as t

from flask.json.provider import DefaultJSONProvider

import msgspec

_encoder = msgspec.json.Encoder()
_decoder = msgspec.json.Decoder()


class MsgSpecJSONProvider(DefaultJSONProvider):
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
        return _decoder.decode(s)

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:  # noqa: ANN401
        return _encoder.encode(obj).decode('utf-8')
