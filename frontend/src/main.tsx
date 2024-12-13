import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { Provider } from "@/components/ui/provider";
import { BrowserRouter } from "react-router-dom";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Provider attribute="class" defaultTheme="dark" forcedTheme="dark">
      <App />
    </Provider>
  </BrowserRouter>
);
