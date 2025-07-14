import Ajv from "ajv";
import addFormats from "ajv-formats";

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

// JSON Schemas (placeholders, replace with actual schemas)
const a2aMessageEnvelopeSchema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "A2A Message Envelope",
  "type": "object",
  "required": ["jsonrpc", "id", "method", "params"],
  "properties": {
    "jsonrpc": { "type": "string", "enum": ["2.0"] },
    "id": { "type": "string" },
    "method": { "type": "string" },
    "params": { "type": "object" }
  }
};

const validateA2AMessageEnvelope = ajv.compile(a2aMessageEnvelopeSchema);

export function validateMessageEnvelope(data: any): { valid: boolean; errors?: any } {
  const valid = validateA2AMessageEnvelope(data);
  return { valid, errors: validateA2AMessageEnvelope.errors };
}

// Additional schema validators can be added here similarly

// Example usage
if (require.main === module) {
  const sampleData = {
    jsonrpc: "2.0",
    id: "1234",
    method: "Agent.Message",
    params: {
      to: "agent1",
      from: "agent2",
      intent: "PlanProject",
      payload: {}
    }
  };

  const result = validateMessageEnvelope(sampleData);
  if (!result.valid) {
    console.error("Validation errors:", result.errors);
  } else {
    console.log("Sample data is valid.");
  }
}
