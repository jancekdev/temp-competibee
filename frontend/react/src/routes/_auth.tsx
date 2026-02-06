import { createFileRoute } from "@tanstack/react-router";
import { getAuth } from "@/lib/allauth";
export const Route = createFileRoute("/_auth")({
  beforeLoad: async ({ location }) => {
    const auth = await getAuth();
    if (!auth?.meta?.is_authenticated) {
      // Instead of using TanStack redirect, navigate to Django's URL directly
      window.location.href = `/accounts/login/?next=${encodeURIComponent(
        location.href
      )}`;
      // Return a temporary value to satisfy TypeScript
      return {};
    }
  },
});
