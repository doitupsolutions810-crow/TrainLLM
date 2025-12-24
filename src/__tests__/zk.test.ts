import { zkAttest } from '../zk';

describe('zk placeholder', () => {
  test('deterministic hash', () => {
    const a = zkAttest('action1', 's');
    const b = zkAttest('action1', 's');
    expect(a).toBe(b);
  });
});
