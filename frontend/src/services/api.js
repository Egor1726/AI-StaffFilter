const API_BASE_URL = "http://localhost:8080";

export async function uploadResumes(archiveFile, requirementsFile) {
  const formData = new FormData();
  formData.append("archive", archiveFile);
  formData.append("requirements", requirementsFile);

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/resumes/upload`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Не удалось подключиться к backend. Проверьте, запущен ли сервер на localhost:8080."
    );
  }

  if (!response.ok) {
    let errorMessage = "Ошибка при загрузке файлов.";

    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.error || errorMessage;
    } catch {
      try {
        errorMessage = await response.text();
      } catch {
        errorMessage = "Не удалось обработать ошибку сервера.";
      }
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

export async function downloadResult(taskId, fileName = "result.txt") {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/resumes/result/${taskId}`);
  } catch {
    throw new Error(
      "Не удалось подключиться к backend при скачивании результата."
    );
  }

  if (!response.ok) {
    let errorMessage = "Ошибка при скачивании результата.";

    try {
      errorMessage = await response.text();
    } catch {
      errorMessage = "Не удалось обработать ошибку сервера.";
    }

    throw new Error(errorMessage);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  window.URL.revokeObjectURL(url);
}