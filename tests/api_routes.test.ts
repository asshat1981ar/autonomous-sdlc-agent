import request from 'supertest';
import app from '../src/app'; // Assuming Express app is exported from src/app.ts

describe('API Routes Test Suite', () => {
  it('should return health status', async () => {
    const res = await request(app).get('/api/v1/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toBe('healthy');
  });

  it('should return version info', async () => {
    const res = await request(app).get('/api/v1/version');
    expect(res.statusCode).toEqual(200);
    expect(res.body.version).toBeDefined();
  });

  it('should require auth for protected routes', async () => {
    const res = await request(app).get('/api/v1/tasks');
    expect(res.statusCode).toEqual(401);
  });

  it('should return 501 for unimplemented POST /api/v1/tasks', async () => {
    const res = await request(app).post('/api/v1/tasks').send({});
    expect(res.statusCode).toEqual(501);
  });

  // Add more tests for other routes similarly
});
