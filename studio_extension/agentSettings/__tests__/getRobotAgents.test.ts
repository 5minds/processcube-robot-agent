import * as fs from 'fs';
import { getRobotAgents, RobotAgent, SOLUTION_ROBOT_DIRECTORY, AGENT_CONFIG_FILE_NAME } from '../getRobotAgents';

// Mock fs module
jest.mock('fs');

const mockFs = fs as jest.Mocked<typeof fs>;

const mockStudio = {
  solution: {
    getSolution: jest.fn(),
  },
  files: {
    getLocalFilenameForUri: jest.fn(),
    getUriForFilename: jest.fn(),
    watchFile: jest.fn(),
  },
};

describe('getRobotAgents', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset module state
    jest.resetModules();
  });

  describe('initialization', () => {
    it('should return null if no solution is open', () => {
      mockStudio.solution.getSolution.mockReturnValue(undefined);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toBeNull();
    });

    it('should create config file if it does not exist', () => {
      mockStudio.solution.getSolution.mockReturnValue({
        baseUri: 'file:///workspace',
      });
      mockStudio.files.getLocalFilenameForUri.mockReturnValue(
        '/workspace/.processcube/robot-agent/'
      );
      mockFs.existsSync.mockReturnValue(false);
      mockFs.mkdirSync.mockImplementation(() => '');
      mockFs.writeFileSync.mockImplementation(() => {});
      mockFs.readFileSync.mockReturnValue(JSON.stringify({ agents: [] }));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      getRobotAgents(mockStudio as any);

      expect(mockFs.mkdirSync).toHaveBeenCalledWith(
        '/workspace/.processcube/robot-agent/',
        { recursive: true }
      );
      expect(mockFs.writeFileSync).toHaveBeenCalledWith(
        '/workspace/.processcube/robot-agent/agents.json',
        JSON.stringify({ agents: [] })
      );
    });

    it('should not create config file if it already exists', () => {
      mockStudio.solution.getSolution.mockReturnValue({
        baseUri: 'file:///workspace',
      });
      mockStudio.files.getLocalFilenameForUri.mockReturnValue(
        '/workspace/.processcube/robot-agent/'
      );
      mockFs.existsSync.mockReturnValue(true);
      mockFs.readFileSync.mockReturnValue(JSON.stringify({ agents: [] }));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      getRobotAgents(mockStudio as any);

      expect(mockFs.mkdirSync).not.toHaveBeenCalled();
      expect(mockFs.writeFileSync).not.toHaveBeenCalled();
    });
  });

  describe('file watching', () => {
    it('should watch the agent config file', () => {
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

      expect(mockStudio.files.watchFile).toHaveBeenCalledWith(
        'file:///workspace/.processcube/robot-agent/agents.json',
        expect.any(Function)
      );
    });

    it('should reload agents when file changes', () => {
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

      const newAgents = { agents: [{ uuid: '123', name: 'Agent 1', url: 'http://localhost' }] };
      mockFs.readFileSync.mockReturnValue(JSON.stringify(newAgents));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toEqual(newAgents);
    });
  });

  describe('agent data management', () => {
    it('should parse and return agent data from config file', () => {
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

      const agents = {
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
          { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
        ],
      };
      mockFs.readFileSync.mockReturnValue(JSON.stringify(agents));
      mockStudio.files.watchFile.mockReturnValue({} as any);

      const result = getRobotAgents(mockStudio as any);

      expect(result).toEqual(agents);
      expect(result?.agents).toHaveLength(2);
    });

    it('should handle malformed JSON in config file', () => {
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
      mockFs.readFileSync.mockReturnValue('invalid json');
      mockStudio.files.watchFile.mockReturnValue({} as any);

      expect(() => getRobotAgents(mockStudio as any)).toThrow();
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
});