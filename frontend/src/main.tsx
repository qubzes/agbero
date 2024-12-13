import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { Provider } from "@/components/ui/provider";

createRoot(document.getElementById("root")!).render(
  <Provider attribute="class" defaultTheme="dark" forcedTheme="dark">
    <App />
  </Provider>
);
