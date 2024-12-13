import { VStack } from "@chakra-ui/react";
import Header from "./components/layout/header";
import Chat from "./components/layout/chat";

function App() {
  return (
    <VStack height="100vh" width="100vw">
      <Header />
      <Chat />
    </VStack>
  );
}

export default App;
