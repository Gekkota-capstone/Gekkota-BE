# /util/swagger_util.py

import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from util.config_util import is_test_mode


def setup_swagger(app: FastAPI):
    """
    Swagger UI 및 OpenAPI 스키마 설정을 커스터마이징하는 함수
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Capstone API",
            version="1.0.0",
            description="Capstone 프로젝트 API 문서\n\n"
                        "## 인증 방법\n\n"
                        "### 프로덕션 모드 (TEST_MODE=False)\n"
                        "- Authorization 헤더에 `Bearer {firebase_token}` 형식으로 Firebase ID 토큰을 전달해야 합니다.\n\n"
                        "### 테스트 모드 (TEST_MODE=True)\n"
                        "- X-Firebase-UID 헤더에 테스트용 사용자 ID를 직접 전달할 수 있습니다.\n"
                        "- 이 모드는 개발 및 테스트 환경에서만 사용해야 합니다.",
            routes=app.routes,
        )

        # 테스트 모드에서만 X-Firebase-UID 헤더 추가
        if is_test_mode():
            # 보안 스키마에 X-Firebase-UID 헤더 추가
            if "components" not in openapi_schema:
                openapi_schema["components"] = {}
            if "securitySchemes" not in openapi_schema["components"]:
                openapi_schema["components"]["securitySchemes"] = {}

            openapi_schema["components"]["securitySchemes"]["X-Firebase-UID"] = {
                "type": "apiKey",
                "in": "header",
                "name": "X-Firebase-UID",
                "description": "테스트 모드에서만 사용: 테스트용 Firebase UID를 직접 전달"
            }

            # Bearer 인증도 함께 추가 (선택적)
            openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "프로덕션 모드에서 사용: Firebase ID 토큰"
            }

            # 모든 경로에 보안 요구사항 추가
            for path in openapi_schema["paths"]:
                for method in openapi_schema["paths"][path]:
                    if method.lower() != "options":  # OPTIONS 요청 제외
                        if openapi_schema["paths"][path][method].get("security") is None:
                            openapi_schema["paths"][path][method]["security"] = []
                        openapi_schema["paths"][path][method]["security"].append(
                            {"X-Firebase-UID": []}
                        )
                        openapi_schema["paths"][path][method]["security"].append(
                            {"BearerAuth": []}
                        )
        else:
            # 프로덕션 모드에서는 Bearer 인증만 추가
            if "components" not in openapi_schema:
                openapi_schema["components"] = {}
            if "securitySchemes" not in openapi_schema["components"]:
                openapi_schema["components"]["securitySchemes"] = {}

            openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Firebase ID 토큰"
            }

            # 모든 경로에 보안 요구사항 추가
            for path in openapi_schema["paths"]:
                for method in openapi_schema["paths"][path]:
                    if method.lower() != "options":  # OPTIONS 요청 제외
                        if openapi_schema["paths"][path][method].get("security") is None:
                            openapi_schema["paths"][path][method]["security"] = []
                        openapi_schema["paths"][path][method]["security"].append(
                            {"BearerAuth": []}
                        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi