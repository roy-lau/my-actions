package top.misec.task;

import com.google.gson.JsonObject;
import lombok.extern.log4j.Log4j2;
import top.misec.apiquery.ApiList;
import top.misec.utils.HttpUtil;

import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Random;

import static top.misec.task.TaskInfoHolder.calculateUpgradeDays;
import static top.misec.task.TaskInfoHolder.STATUS_CODE_STR;

/**
 * @author @JunzhouLiu @Kurenai
 * @create 2020/10/11 20:44
 */
@Log4j2
public class DailyTask {

    private final List<Task> dailyTasks = Arrays.asList(
            new UserCheck(),
            new VideoWatch(),
            new MangaSign(),
            new CoinAdd(),
            // new Silver2coin(), // 银瓜子兑换硬币接口 405
            new LiveCheckin(),
            new GiveGift(),
            new ChargeMe(),
            new GetVipPrivilege()
    );

    public void doDailyTask() {
        try {
            printTime();
            log.debug("任务启动中");
            for (Task task : dailyTasks) {
                log.info("---🚩{}开始🚩-----", task.getName());
                task.run();
                log.info("-----{}结束------\n", task.getName());
                taskSuspend();
            }
            log.info("本日任务已全部执行完毕");
            calculateUpgradeDays();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            ServerPush.doServerPush();
        }
    }

    /**
     * @return jsonObject 返回status对象，包含{"login":true,"watch":true,"coins":50,
     * "share":true,"email":true,"tel":true,"safe_question":true,"identify_card":false}
     * @author @srcrs
     */
    public static JsonObject getDailyTaskStatus() {
        JsonObject jsonObject = HttpUtil.doGet(ApiList.reward);
        int responseCode = jsonObject.get(STATUS_CODE_STR).getAsInt();
        if (responseCode == 0) {
            log.info("请求本日任务完成状态成功");
            return jsonObject.get("data").getAsJsonObject();
        } else {
            log.debug(jsonObject.get("message").getAsString());
            return HttpUtil.doGet(ApiList.reward).get("data").getAsJsonObject();
            //偶发性请求失败，再请求一次。
        }
    }

    private void printTime() {
        Date d = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        String time = sdf.format(d);
        log.info(time);
    }

    private void taskSuspend() throws InterruptedException {
        Random random = new Random();
        int sleepTime = (int) ((random.nextDouble() + 0.5) * 3000);
        log.info("-----随机暂停{}ms-----\n", sleepTime);
        Thread.sleep(sleepTime);
    }

}

