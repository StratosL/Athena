import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Dashboard } from "@/pages-new/Dashboard"
import { Settings } from "@/pages-new/Settings"
import { Analytics } from "@/pages-new/Analytics"
import { Tasks } from "@/pages-new/Tasks"
import { DailyPlan } from "@/pages-new/DailyPlan"
import { Pomodoro } from "@/pages-new/Pomodoro"
import { Onboarding } from "@/pages-new/Onboarding"
import { DailyReflection } from "@/pages-new/DailyReflection"
import { Guide } from "@/pages-new/Guide"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/daily-plan" element={<DailyPlan />} />
          <Route path="/pomodoro" element={<Pomodoro />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/guide" element={<Guide />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/reflection" element={<DailyReflection />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
