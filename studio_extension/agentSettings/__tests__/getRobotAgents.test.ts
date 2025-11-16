import * as fs from 'fs';

// Mock fs module BEFORE importing getRobotAgents
jest.mock('fs');

const mockFs = fs as jest.Mocked<typeof fs>;

// Import AFTER mocking fs
import { SOLUTION_ROBOT_DIRECTORY, AGENT_CONFIG_FILE_NAME } from '../getRobotAgents';

const createMockStudio = () => ({
  solution: {
    getSolution: jest.fn(),
  },
  files: {
    getLocalFilenameForUri: jest.fn(),
    getUriForFilename: jest.fn(),
    watchFile: jest.fn(),
  },
});

describe('getRobotAgents', () => {
  let mockStudio: ReturnType<typeof createMockStudio>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockStudio = createMockStudio();
  });

  describe('constants', () => {
    it('should define correct directory path', () => {
      expect(SOLUTION_ROBOT_DIRECTORY).toBe('/.processcube/robot-agent/');
    });

    it('should define correct config file name', () => {
      expect(AGENT_CONFIG_FILE_NAME).toBe('agents.json');
    });
  });

  describe('initialization', () => {
    it('should return null when no solution is open', () => {
      // Import at test level to get fresh module state
      const { getRobotAgents } = require('../getRobotAgents');

      mockStudio.solution.getSolution.mockReturnValue(undefined);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toBeNull();
    });

    it('should handle file watching setup', () => {
      const { getRobotAgents } = require('../getRobotAgents');

      const testAgents = { agents: [{ uuid: '1', name: 'Agent 1', url: 'http://localhost' }] };

      mockStudio.solution.getSolution.mockReturnValue({
        baseUri: 'file:///workspace',
      });
      mockStudio.files.getLocalFilenameForUri.mockReturnValue(
        '/workspace/.processcube/robot-agent/'
      );
      mockStudio.files.getUriForFilename.mockReturnValue(
        'file:///workspace/.processcube/robot-agent/agents.json'
      );
      mockFs.existsSync.mockReturnValue(true);
      mockFs.readFileSync.mockReturnValue(JSON.stringify(testAgents) as any);
      mockStudio.files.watchFile.mockReturnValue({} as any);

      const result = getRobotAgents(mockStudio as any);

      // Component should initialize without errors
      expect(mockStudio.files.getLocalFilenameForUri).toHaveBeenCalled();
    });
  });
});