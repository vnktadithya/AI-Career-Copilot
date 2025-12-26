import { ActivityEventType } from "./eventType";
import { sendEvent } from "../transport/eventSender";
import { hashObject } from "../utils/hash";

export async function buildAndSendEvent(
  type: ActivityEventType,
  payload: Record<string, any>
) {
  const event = {
    event_type: type,
    payload,
    timestamp: new Date().toISOString(),
    dedupe_key: hashObject({ type, payload })
  };

  await sendEvent(event);
}
