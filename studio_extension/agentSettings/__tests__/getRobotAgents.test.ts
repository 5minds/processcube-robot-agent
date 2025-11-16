import * as fs from 'fs';

// Mock fs module BEFORE importing getRobotAgents
jest.mock('fs');

const mockFs = fs as jest.Mocked<typeof fs>;

// Import AFTER mocking fs
import { getRobotAgents, RobotAgent, SOLUTION_ROBOT_DIRECTORY, AGENT_CONFIG_FILE_NAME } from '../getRobotAgents';

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

  describe('initialization', () => {
    it('should return null if no solution is open', () => {
      mockStudio.solution.getSolution.mockReturnValue(undefined);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toBeNull();
    });

    it('should return agents data when available', () => {
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
      mockFs.readFileSync.mockReturnValue(JSON.stringify({ agents: [] }));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toBeDefined();
      expect(result?.agents).toBeDefined();
    });
  });

  describe('constants', () => {
    it('should define correct directory path', () => {
      expect(SOLUTION_ROBOT_DIRECTORY).toBe('/.processcube/robot-agent/');
    });

    it('should define correct config file name', () => {
      expect(AGENT_CONFIG_FILE_NAME).toBe('agents.json');
    });
  });

  describe('file operations', () => {
    it('should attempt to watch agent config file', () => {
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
      mockFs.readFileSync.mockReturnValue(JSON.stringify({ agents: [] }));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      getRobotAgents(mockStudio as any);

      // Verify watch was called
      expect(mockStudio.files.watchFile).toHaveBeenCalled();
    });

    it('should read agent config file', () => {
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

      const testAgents = { agents: [{ uuid: '1', name: 'Agent 1', url: 'http://localhost' }] };
      mockFs.readFileSync.mockReturnValue(JSON.stringify(testAgents));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      const result = getRobotAgents(mockStudio as any);

      expect(mockFs.readFileSync).toHaveBeenCalled();
      expect(result?.agents).toHaveLength(1);
    });
  });
});