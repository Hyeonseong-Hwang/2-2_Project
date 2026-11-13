"""core 패키지가 처음 불러와질 때 가장 먼저 실행됩니다.

맥에서 Firestore(gRPC)가 응답 없이 멈추는 문제를 막기 위해,
gRPC 라이브러리가 불러와지기 전에 DNS 방식을 시스템 기본(native)으로 지정합니다.
"""

import os

os.environ.setdefault("GRPC_DNS_RESOLVER", "native")
