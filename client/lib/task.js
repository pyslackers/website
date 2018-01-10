/**
 * Poll the tasks API for a task result.
 *
 * @param taskId The task id to poll for
 * @param maxTimeout Maximum number of seconds to wait on the result.
 * @returns Body retrieved from the task api
 */
export const retrieveTaskResult = async (taskId, maxTimeout = 15) => {
    let taskResult;
    const start = new Date() / 1000;
    while (new Date() / 1000 - start < maxTimeout) {
        taskResult = await $.ajax({
            url: `/core/tasks/${taskId}`,
            method: 'GET',
        });
        if (taskResult !== undefined) {
            return taskResult;
        }
        await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    throw new Error('Timeout exceeded waiting for task');
};
