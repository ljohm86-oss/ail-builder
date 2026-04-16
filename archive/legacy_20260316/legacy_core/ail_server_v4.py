from flask import Flask, request, jsonify
from ail_engine_v4 import AILParserV4, AILProjectGeneratorV4
import traceback

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_ail():
    try:
        ail_code = request.json.get("ail_code", "")
        if not ail_code:
            return jsonify({"status": "error", "message": "空指令"}), 400

        # V4.0 核心引擎接入（支持鉴权与关系型数据库）
        ast = AILParserV4(ail_code).parse()
        generator = AILProjectGeneratorV4(ast, base_dir="./output_projects")
        project_path = generator.build_project()

        return jsonify({
            "status": "ok",
            "message": f"🚀 V4.0 深水架构编译成功！后端已注入 JWT 鉴权与外键关联。路径：{project_path}"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 AIL V4.0 云端引擎已启动，监听 5000 端口...")
    app.run(port=5000)
