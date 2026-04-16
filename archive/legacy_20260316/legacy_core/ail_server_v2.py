from __future__ import annotations

from flask import Flask, jsonify, request

from ail_compiler_v2_core import AILParserV2
from ail_generator_v2 import AILProjectGenerator

app = Flask(__name__)


@app.post("/compile")
def compile_ail_v2():
    try:
        payload = request.json or {}
        ail_code = payload.get("ail_code")
        if not isinstance(ail_code, str) or not ail_code.strip():
            return jsonify({"status": "error", "message": "ail_code is required"}), 400

        ast = AILParserV2(ail_code).parse()
        generator = AILProjectGenerator(ast, base_dir="./output_projects")
        project_path = generator.build_project()

        return jsonify(
            {
                "status": "ok",
                "message": f"V2.0 架构编译成功！工程已生成至：{project_path}",
            }
        )
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
