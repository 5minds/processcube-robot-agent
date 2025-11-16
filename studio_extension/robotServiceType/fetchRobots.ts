import { SelectOption, Studio } from '@5minds/processcube_studio_sdk';

export type RobotTopic = {
  name: string;
  topic: string;
};

export type RobotSelectOption = Omit<SelectOption, 'value'> & { value: RobotTopic };

const FETCH_TIMEOUT = 2000;

export function fetchRobots(url: string, studio: Studio, withTimeout: boolean): Promise<Array<RobotTopic>> {
  const fetchPromise = studio.http.getJson(`${url}/robot_agents/robots`)
    .then((response) => response.topics as Array<RobotTopic>);

  if (withTimeout) {
    const timerPromise = new Promise<Array<RobotTopic>>((_, reject) => setTimeout(() => reject(`No response from server within ${FETCH_TIMEOUT / 1000} seconds`), FETCH_TIMEOUT));
    return Promise.race([fetchPromise, timerPromise]);
  }

  return fetchPromise;
}
