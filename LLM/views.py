import os
from pathlib import Path
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

from ScholarSHIP import settings

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def analyze_file(request):
    if request.method == "POST":
        try:
            position = request.POST.get("position")
            pdf = request.FILES.get("note", None)
            file_path = default_storage.save(pdf.name, pdf)
            absolute_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            # 调用大模型的API
            api_key = "sk-yIKoTpQejvjffR1Bfv2MmVIqjQsQdbFsKwI0ENOh0IKoEzcH"
            base_url = "https://api.moonshot.cn/v1"
            headers = {"Authorization": f"Bearer {api_key}"}

            with open(absolute_file_path, "rb") as f:
                response = requests.post(
                    f"{base_url}/files",
                    headers=headers,
                    files={"file": f},
                    data={"purpose": "file-extract"},
                )
            if response.status_code == 200:
                file_object = response.json()
                file_id = file_object["id"]

                # 获取文件内容
                content_response = requests.get(
                    f"{base_url}/files/{file_id}/content", headers=headers
                )

                if content_response.status_code == 200:
                    print(content_response.json())
                    file_content = content_response.json()["content"]

                    # 准备消息
                    messages = [
                        {"role": "system", "content": "你是 Kimi"},
                        {"role": "system", "content": file_content},
                        {
                            "role": "user",
                            "content": f"我想要投递{position}岗位，请你帮我优化一下，给出修改建议，谢谢",
                        },
                    ]
                    # 调用 chat-completion
                    completion_response = requests.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json={
                            "model": "moonshot-v1-32k",
                            "messages": messages,
                            "temperature": 0.3,
                        },
                    )

                    if completion_response.status_code == 200:
                        completion = completion_response.json()
                        analysis_result = completion["choices"][0]["message"]
                        return JsonResponse(
                            {"error": 0, "msg": "分析成功", "result": analysis_result}
                        )
                    else:
                        return JsonResponse(
                            {"error": "Error in chat completion API call"}, status=500
                        )
                else:
                    return JsonResponse(
                        {"error": "Error retrieving file content"}, status=500
                    )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})

        else:
            return JsonResponse({"error": "Error uploading file"}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)
