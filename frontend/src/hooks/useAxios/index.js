import axios from "axios";
import { useEffect, useState } from "react";

const useAxios = () => {
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState();

  const axiosInstance = axios.create({
    baseURL: "",
  });

  axiosInstance.interceptors.response.use(
    (config) => {
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  axiosInstance.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  let controller = new AbortController();
  useEffect(() => {
    return () => controller?.abort();
  }, []);

  const fetchData = async ({ url, method, data = {}, params = {} }) => {
    setLoading(true);
    controller.abort();
    controller = new AbortController();

    try {
      const result = await axiosInstance({
        url,
        method,
        data,
        params,
        signal: controller.signal,
      });
      setResponse(result);
    } catch (error) {
      if (axios.isCancel(error)) {
        console.error("Request cancelled", error.message);
      } else {
        setError(error.response ? error.response.data : error.message); 
      }
    } finally {
      setLoading(false);
    }
  };
};
