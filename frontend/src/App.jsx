import { useState, useRef } from "react";
import "./App.css";
import { uploadResumes, downloadResult } from "./services/api";

function App() {
  const [archiveFile, setArchiveFile] = useState(null);
  const [requirementsFile, setRequirementsFile] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Файлы не выбраны");
  const [isArchiveDragActive, setIsArchiveDragActive] = useState(false);
  const [isRequirementsDragActive, setIsRequirementsDragActive] = useState(false);

  const archiveInputRef = useRef(null);
  const requirementsInputRef = useRef(null);

  const validateArchiveFile = (file) => {
    if (!file) {
      return "Файл не выбран.";
    }

    if (!file.name.toLowerCase().endsWith(".zip")) {
      return "Нужно выбрать ZIP-архив с резюме.";
    }

    return "";
  };

  const validateRequirementsFile = (file) => {
    if (!file) {
      return "Файл не выбран.";
    }

    if (!file.name.toLowerCase().endsWith(".txt")) {
      return "Нужно выбрать TXT-файл с требованиями.";
    }

    return "";
  };

  const handleArchiveChange = (event) => {
    const file = event.target.files[0];
    setError("");

    const validationError = validateArchiveFile(file);
    if (validationError) {
      setArchiveFile(null);
      setError(validationError);
      return;
    }

    setArchiveFile(file);
    setStatus("ZIP-архив выбран");
  };

  const handleRequirementsChange = (event) => {
    const file = event.target.files[0];
    setError("");

    const validationError = validateRequirementsFile(file);
    if (validationError) {
      setRequirementsFile(null);
      setError(validationError);
      return;
    }

    setRequirementsFile(file);
    setStatus("TXT-файл выбран");
  };

  const handleArchiveDrop = (event) => {
    event.preventDefault();
    setIsArchiveDragActive(false);
    setError("");

    const file = event.dataTransfer.files[0];
    const validationError = validateArchiveFile(file);

    if (validationError) {
      setArchiveFile(null);
      setError(validationError);
      return;
    }

    setArchiveFile(file);
    setStatus("ZIP-архив выбран");
  };

  const handleRequirementsDrop = (event) => {
    event.preventDefault();
    setIsRequirementsDragActive(false);
    setError("");

    const file = event.dataTransfer.files[0];
    const validationError = validateRequirementsFile(file);

    if (validationError) {
      setRequirementsFile(null);
      setError(validationError);
      return;
    }

    setRequirementsFile(file);
    setStatus("TXT-файл выбран");
  };

  const buildResultFileName = () => {
    if (!requirementsFile) {
      return "result.txt";
    }

    const originalName = requirementsFile.name;
    const lastDotIndex = originalName.lastIndexOf(".");
    const baseName =
      lastDotIndex > 0 ? originalName.slice(0, lastDotIndex) : originalName;

    return `${baseName}_result.txt`;
  };

  const handleSubmit = async () => {
    setError("");

    if (!archiveFile) {
      setError("Сначала выберите ZIP-архив.");
      return;
    }

    if (!requirementsFile) {
      setError("Сначала выберите TXT-файл с требованиями.");
      return;
    }

    setStatus("Отправка файлов на сервер...");

    try {
      const uploadResponse = await uploadResumes(archiveFile, requirementsFile);

      if (!uploadResponse.taskId) {
        throw new Error("Сервер не вернул taskId.");
      }

      setStatus("Файлы обработаны. Скачивание результата...");

      await downloadResult(uploadResponse.taskId, buildResultFileName());

      setStatus("Результат успешно скачан.");
    } catch (err) {
      setError(err.message || "Произошла ошибка.");
      setStatus("Ошибка");
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1>AI Staff Filter</h1>
        <p className="description">
          Загрузите ZIP-архив с резюме и TXT-файл с требованиями к вакансии.
        </p>

        <div className="field">
          <label>ZIP-архив с резюме</label>

          <div
            className={`drop-zone ${isArchiveDragActive ? "drag-active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsArchiveDragActive(true);
            }}
            onDragLeave={() => setIsArchiveDragActive(false)}
            onDrop={handleArchiveDrop}
          >
            <p>Перетащите ZIP-файл сюда или выберите вручную</p>

            <input
              ref={archiveInputRef}
              type="file"
              accept=".zip"
              onChange={handleArchiveChange}
              className="hidden-file-input"
            />

            <button
              type="button"
              className="secondary-button"
              onClick={() => archiveInputRef.current?.click()}
            >
              Выбрать ZIP-файл
            </button>
          </div>

          <div className="file-name">
            {archiveFile ? archiveFile.name : "Файл не выбран"}
          </div>
        </div>

        <div className="field">
          <label>TXT-файл с требованиями</label>

          <div
            className={`drop-zone ${isRequirementsDragActive ? "drag-active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsRequirementsDragActive(true);
            }}
            onDragLeave={() => setIsRequirementsDragActive(false)}
            onDrop={handleRequirementsDrop}
          >
            <p>Перетащите TXT-файл сюда или выберите вручную</p>

            <input
              ref={requirementsInputRef}
              type="file"
              accept=".txt"
              onChange={handleRequirementsChange}
              className="hidden-file-input"
            />

            <button
              type="button"
              className="secondary-button"
              onClick={() => requirementsInputRef.current?.click()}
            >
              Выбрать TXT-файл
            </button>
          </div>

          <div className="file-name">
            {requirementsFile ? requirementsFile.name : "Файл не выбран"}
          </div>
        </div>

        <button onClick={handleSubmit}>Отправить</button>

        <div className="status">
          <strong>Статус:</strong> {status}
        </div>

        {error && <div className="error">{error}</div>}
      </div>
    </div>
  );
}

export default App;