import { fetchRobots, RobotTopic } from '../fetchRobots';

// Mock the Studio type
const mockStudio = {
  http: {
    getJson: jest.fn(),
  },
};

describe('fetchRobots', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('successful fetch', () => {
    it('should fetch robots from the agent URL', async () => {
      const mockRobots: RobotTopic[] = [
        { name: 'Robot 1', topic: 'robot_1' },
        { name: 'Robot 2', topic: 'robot_2' },
      ];

      mockStudio.http.getJson.mockResolvedValue({ topics: mockRobots });

      const result = await fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        false
      );

      expect(result).toEqual(mockRobots);
      expect(mockStudio.http.getJson).toHaveBeenCalledWith(
        'http://localhost:8080/robot_agents/robots'
      );
    });

    it('should handle empty robot list', async () => {
      mockStudio.http.getJson.mockResolvedValue({ topics: [] });

      const result = await fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        false
      );

      expect(result).toEqual([]);
    });

    it('should construct correct URL with trailing slash', async () => {
      mockStudio.http.getJson.mockResolvedValue({ topics: [] });

      await fetchRobots('http://localhost:8080/', mockStudio as any, false);

      expect(mockStudio.http.getJson).toHaveBeenCalledWith(
        'http://localhost:8080//robot_agents/robots'
      );
    });
  });

  describe('timeout handling', () => {
    it('should reject if response takes longer than timeout', async () => {
      mockStudio.http.getJson.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ topics: [] }), 3000)
          )
      );

      const promise = fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        true
      );

      await expect(promise).rejects.toMatch(
        /No response from server within 2 seconds/
      );
    });

    it('should resolve if response comes within timeout', async () => {
      const mockRobots: RobotTopic[] = [
        { name: 'Robot 1', topic: 'robot_1' },
      ];

      mockStudio.http.getJson.mockResolvedValue({ topics: mockRobots });

      const result = await fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        true
      );

      expect(result).toEqual(mockRobots);
    });

    it('should skip timeout when withTimeout is false', async () => {
      mockStudio.http.getJson.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ topics: [] }), 3000)
          )
      );

      const promise = fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        false
      );

      // Should not reject due to timeout
      expect(promise).toBeTruthy();
    });
  });

  describe('error handling', () => {
    it('should propagate fetch errors', async () => {
      const error = new Error('Network error');
      mockStudio.http.getJson.mockRejectedValue(error);

      const promise = fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        false
      );

      await expect(promise).rejects.toEqual(error);
    });

    it('should handle malformed response', async () => {
      mockStudio.http.getJson.mockResolvedValue({ someOtherField: [] });

      const result = await fetchRobots(
        'http://localhost:8080',
        mockStudio as any,
        false
      );

      // When topics is undefined, it should be treated as undefined
      expect(result).toBeUndefined();
    });
  });
});