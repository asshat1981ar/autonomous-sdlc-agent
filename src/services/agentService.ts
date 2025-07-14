import { getSession } from './neo4jClient';

export async function registerAgent(agentData: any) {
  const session = getSession();
  try {
    const result = await session.run(
      'MERGE (a:Agent {id: $id}) SET a += $props RETURN a',
      { id: agentData.id, props: agentData }
    );
    return result.records[0].get('a').properties;
  } finally {
    await session.close();
  }
}

export async function getAgentById(agentId: string) {
  const session = getSession();
  try {
    const result = await session.run(
      'MATCH (a:Agent {id: $id}) RETURN a',
      { id: agentId }
    );
    if (result.records.length === 0) return null;
    return result.records[0].get('a').properties;
  } finally {
    await session.close();
  }
}

export async function listAgents() {
  const session = getSession();
  try {
    const result = await session.run('MATCH (a:Agent) RETURN a');
    return result.records.map(record => record.get('a').properties);
  } finally {
    await session.close();
  }
}

export async function updateAgent(agentId: string, updateData: any) {
  const session = getSession();
  try {
    const result = await session.run(
      'MATCH (a:Agent {id: $id}) SET a += $props RETURN a',
      { id: agentId, props: updateData }
    );
    if (result.records.length === 0) return null;
    return result.records[0].get('a').properties;
  } finally {
    await session.close();
  }
}

export async function removeAgent(agentId: string) {
  const session = getSession();
  try {
    await session.run(
      'MATCH (a:Agent {id: $id}) DETACH DELETE a',
      { id: agentId }
    );
    return true;
  } finally {
    await session.close();
  }
}
