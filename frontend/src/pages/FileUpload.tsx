import { Cancel, PictureAsPdfSharp, UploadFile } from "@mui/icons-material";
import { useState, useRef } from "react";
import Logo from '../assets/Logo.svg';
import axios from "axios";
import { Button, createTheme, ThemeProvider } from "@mui/material";


const acceptedFileExtensions = ["pdf"];
const theme = createTheme({
  palette: {
    primary: {
      main: '#ea7f1f',
    },
    secondary: {
      main: '#E0C2FF',
      light: '#F5EBFF',
      contrastText: '#47008F',
    },
  },
});

const Uploader: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [error, setError] = useState<string>("");

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const acceptedFileTypesString = acceptedFileExtensions
    .map((ext) => `.${ext}`)
    .join(",");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      processFiles(Array.from(event.target.files));
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files) {
      processFiles(Array.from(event.dataTransfer.files));
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("file", file);
    });

    try {
      const response = await axios.post("http://localhost:8000/knowledge-base/corpus/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      alert("Upload successful");
    } catch (error) {
      console.error("Upload error:", error);
    }
  };

  const processFiles = (filesArray: File[]) => {
    let hasError = false;
    const newSelectedFiles = [...selectedFiles];

    filesArray.forEach((file) => {
      const fileExtension = file.name.split(".").pop()?.toLowerCase();
      if (!fileExtension || !acceptedFileExtensions.includes(fileExtension)) {
        hasError = true;
        setError(`Only ${acceptedFileExtensions.join(", ")} files are allowed`);
      } else if (newSelectedFiles.some((f) => f.name === file.name)) {
        hasError = true;
        setError("File names must be unique");
      } else {
        newSelectedFiles.push(file);
      }
    });

    if (!hasError) {
      setError("");
      setSelectedFiles(newSelectedFiles);
    }
  };

  const handleCustomButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileDelete = (index: number) => {
    setSelectedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  return (
    <div className="font-urbanist">
        <div className="flex items- animate-fade-in justify-center">   
              <img src={Logo} alt="Kifiya Logo" className="w-16 h-16 md:w-24 h-24" />
          </div>
     <div className="flex justify-center items-center bg-gray-100">
        
      <div className="w-full max-w-5xl p-8 bg-white shadow-lg">
        <h2 className="text-2xl font-semibold text-center mb-2">
          Upload Files
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            className="min-h-[23rem] border-4 border-dashed border-blue-500 bg-blue-100 rounded-3xl p-4 flex flex-col justify-center items-center space-y-4"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e)}
          >
            <UploadFile />
            <p className="text-lg font-semibold">Drag and Drop the files</p>
            <p className="text-lg font-bold">or</p>
            <button
              type="button"
              onClick={handleCustomButtonClick}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:bg-blue-600"
            >
              Upload Files
            </button>
            <input
              type="file"
              id="files"
              name="files"
              multiple
              accept={acceptedFileTypesString}
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileChange}
              onClick={(event) => {
                const inputElement = event.target as HTMLInputElement;
                inputElement.value = "";
                }}
            />
          </div>

          <div className="border-2 border-gray-300 rounded-3xl max-h-[23rem] overflow-auto">
            {selectedFiles.length > 0 ? (
              <ul className="px-4">
                {selectedFiles.map((file, index) => (
                  <li
                    key={file.name}
                    className="flex justify-between items-center border-b py-2"
                  >
                    <div className="flex items-center">
                        <PictureAsPdfSharp />
                      <span className="text-base px-4">{file.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleFileDelete(index)}
                      className="text-red-500 hover:text-red-700 focus:outline-none"
                    >
                      <Cancel />
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="h-full flex justify-center items-center">
                <p className="text-lg font-semibold text-gray-500 text-center">
                  No Files Uploaded Yet
                </p>
              </div>
            )}
          </div>
        </div>
        {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
        <div className="flex justify-center mt-8">
          <ThemeProvider theme={theme}>
              <Button
                fullWidth
                type="submit"
                variant="contained"
                color="primary"
                className="mt-8 h-12"
                onClick={handleUpload}
            >
                Upload
              </Button>
            </ThemeProvider>
        </div>
      </div>
    </div>
    </div>

  );
};

export default Uploader;