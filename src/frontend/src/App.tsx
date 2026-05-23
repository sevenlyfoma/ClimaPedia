import {
  Navigate,
  RouterProvider,
  createBrowserRouter,
} from "react-router-dom";
import { MapPage } from "./map/MapPage";
import "./App.css";
import { Root } from "./Root";
import { ChartPage } from "./chart/ChartPage";
import { TimelinePage } from "./timeline/TimelinePage";

/* Import CSS files for different accessibility settings */
import "./accessibility.css";

function App() {
  // This defines our websites routing structure
  // Single root for shared content, and each child is a separate page
  const router = createBrowserRouter([
    {
      path: "/",
      element: <Root />,
      children: [
        {
          path: "",
          element: <MapPage />,
        },
        {
          path: "/Chart",
          element: <ChartPage />,
        },
        {
          path: "/Map",
          element: <Navigate to="/" replace />,
        },
        {
          path: "/Timeline",
          element: <TimelinePage />,
        },
      ],
    },
  ]);

  return <RouterProvider router={router} />;
}

export default App;
