import { RobotAgentsConfigDocument } from '../RobotAgentsConfigDocument';
import { RobotAgents } from '../getRobotAgents';

// Mock EditorDocumentModel
jest.mock('@5minds/processcube_studio_sdk', () => ({
  EditorDocumentModel: class EditorDocumentModel {
    protected uri: string;
    protected originalData: string = '';
    protected currentData: string = '';

    constructor(uri: string) {
      this.uri = uri;
    }

    protected updateOriginalAndCurrentData(original: string, current: string): void {
      this.originalData = original;
      this.currentData = current;
    }

    protected updateCurrentData(data: string): void {
      this.currentData = data;
    }

    protected getCurrentData(): string {
      return this.currentData;
    }

    protected getUri(): string {
      return this.uri;
    }
  },
}));

describe('RobotAgentsConfigDocument', () => {
  const testUri = 'file:///workspace/.processcube/robot-agent/agents.json';
  const testData = JSON.stringify({
    agents: [
      { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
    ],
  });

  describe('constructor', () => {
    it('should initialize with URI and data', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);

      expect(doc).toBeTruthy();
      expect((doc as any).uri).toBe(testUri);
    });

    it('should use original data if no restored data provided', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);

      expect(doc.getValue()).toEqual(JSON.parse(testData));
    });

    it('should use restored data if provided', () => {
      const restoredData = JSON.stringify({
        agents: [
          { uuid: '2', name: 'Restored Agent', url: 'http://localhost:9000' },
        ],
      });

      const doc = new RobotAgentsConfigDocument(testUri, testData, restoredData);

      expect(doc.getValue()).toEqual(JSON.parse(restoredData));
    });

    it('should use original data if restored data is null', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData, null);

      expect(doc.getValue()).toEqual(JSON.parse(testData));
    });
  });

  describe('getValue', () => {
    it('should parse and return agent data', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);
      const value = doc.getValue();

      expect(value).toEqual(JSON.parse(testData));
      expect(value.agents).toHaveLength(1);
      expect(value.agents[0].name).toBe('Agent 1');
    });

    it('should return empty agents list for empty data', () => {
      const emptyData = JSON.stringify({ agents: [] });
      const doc = new RobotAgentsConfigDocument(testUri, emptyData);
      const value = doc.getValue();

      expect(value.agents).toEqual([]);
    });

    it('should handle multiple agents', () => {
      const multiAgentData = JSON.stringify({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
          { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
          { uuid: '3', name: 'Agent 3', url: 'http://localhost:8082' },
        ],
      });

      const doc = new RobotAgentsConfigDocument(testUri, multiAgentData);
      const value = doc.getValue();

      expect(value.agents).toHaveLength(3);
    });
  });

  describe('setValue', () => {
    it('should set and stringify agent data', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);
      const newData: RobotAgents = {
        agents: [
          { uuid: '2', name: 'New Agent', url: 'http://localhost:9000' },
        ],
      };

      doc.setValue(newData);

      expect(doc.getValue()).toEqual(newData);
    });

    it('should format JSON with 2-space indentation', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);
      const newData: RobotAgents = {
        agents: [
          { uuid: '1', name: 'Test', url: 'http://localhost' },
        ],
      };

      doc.setValue(newData);
      const stringified = (doc as any).getCurrentData();

      // Check that it's properly formatted
      expect(stringified).toContain('  ');
      expect(stringified).toContain('\n');
    });

    it('should replace existing data', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);

      const newData1: RobotAgents = {
        agents: [{ uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' }],
      };
      doc.setValue(newData1);
      expect(doc.getValue()).toEqual(newData1);

      const newData2: RobotAgents = {
        agents: [
          { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
          { uuid: '3', name: 'Agent 3', url: 'http://localhost:8082' },
        ],
      };
      doc.setValue(newData2);
      expect(doc.getValue()).toEqual(newData2);
    });

    it('should handle empty agents list', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);
      const newData: RobotAgents = { agents: [] };

      doc.setValue(newData);

      expect(doc.getValue()).toEqual(newData);
      expect(doc.getValue().agents).toHaveLength(0);
    });
  });

  describe('static create method', () => {
    it('should create document from file loader', async () => {
      const mockFileLoader = {
        load: jest.fn().mockResolvedValue(testData),
      };

      const doc = await RobotAgentsConfigDocument.create(
        testUri,
        null,
        null,
        mockFileLoader
      );

      expect(mockFileLoader.load).toHaveBeenCalledWith(testUri);
      expect(doc).toBeInstanceOf(RobotAgentsConfigDocument);
      expect(doc.getValue()).toEqual(JSON.parse(testData));
    });

    it('should use restored data if provided to create', async () => {
      const restoredData = JSON.stringify({
        agents: [{ uuid: '99', name: 'Restored', url: 'http://restored' }],
      });

      const mockFileLoader = {
        load: jest.fn().mockResolvedValue(testData),
      };

      const doc = await RobotAgentsConfigDocument.create(
        testUri,
        restoredData,
        null,
        mockFileLoader
      );

      expect(doc.getValue()).toEqual(JSON.parse(restoredData));
    });
  });

  describe('data persistence', () => {
    it('should maintain data across multiple getValue calls', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);

      const value1 = doc.getValue();
      const value2 = doc.getValue();

      expect(value1).toEqual(value2);
    });

    it('should persist changes made via setValue', () => {
      const doc = new RobotAgentsConfigDocument(testUri, testData);
      const newData: RobotAgents = {
        agents: [{ uuid: '5', name: 'Changed', url: 'http://changed' }],
      };

      doc.setValue(newData);
      const retrievedValue = doc.getValue();

      expect(retrievedValue).toEqual(newData);
      expect(retrievedValue.agents[0].name).toBe('Changed');
    });
  });
});