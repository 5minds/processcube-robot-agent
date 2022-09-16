import { EditorDocumentModel, Studio } from '@atlas-engine/atlas_studio_sdk';
import { RobotAgents } from './getRobotAgents';

export class RobotAgentsConfigDocument extends EditorDocumentModel {
  constructor(uri: string, originalData: string, restoredCurrentData: string | null = null) {
    super(uri);

    this.updateOriginalAndCurrentData(originalData, restoredCurrentData || originalData);
  }

  static async create(uri, restoredCurrentData, restoredMetadata, fileLoader, studio): Promise<RobotAgentsConfigDocument> {
    const content = await fileLoader.load(uri);

    return new RobotAgentsConfigDocument(uri, content, restoredCurrentData);
  }

  setValue(data: RobotAgents): void {
    const stringifiedData = JSON.stringify(data, null, 2);
    this.updateCurrentData(stringifiedData);
  }

  getValue(): RobotAgents {
    return JSON.parse(this.getCurrentData());
  }
}
