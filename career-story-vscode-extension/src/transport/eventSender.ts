import { getAuthToken } from "../auth/session";
import { BACKEND_URL } from "../config";

export async function sendEvent(event: any) {
  const token = await getAuthToken();
  if (!token) return; // silently skip if not logged in

  await fetch(`${BACKEND_URL}/api/v1/webhooks/vscode`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(event)
  });
}
