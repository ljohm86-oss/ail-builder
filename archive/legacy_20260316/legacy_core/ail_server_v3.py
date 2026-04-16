from flask import Flask, request, jsonify
from ail_engine_v3 import AILParserV3, AILProjectGeneratorV3
import traceback

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_ail():
    try:
        ail_code = request.json.get("ail_code", "")
        if not ail_code:
            return jsonify({"status": "error", "message": "空指令"}), 400

        # V3.0 核心引擎接入
        ast = AILParserV3(ail_code).parse()
        generator = AILProjectGeneratorV3(ast, base_dir="./output_projects")
        project_path = generator.build_project()

        return jsonify({
            "status": "ok",
            "message": f"🚀 V3.0 架构编译成功！UI装配脚本已生成。路径：{project_path}"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 AIL V3.0 云端引擎已启动，监听 5000 端口...")
    app.run(port=5000)
