"""故障后自动修复 Skill"""
import logging
from src.skills.models import SkillDSL
from src.skills.storage import SkillStorage


class AutoReparer:
    """自动修复器"""

    def __init__(self, skill_storage: SkillStorage, ai_repairer=None):
        self.skill_storage = skill_storage
        self.ai_repairer = ai_repairer
        self.logger = logging.getLogger("blockmind.auto_repair")

    async def repair(self, failed_skill: SkillDSL, error: Exception) -> SkillDSL:
        """修复失败的 Skill"""
        self.logger.info(f"🔧 开始修复 Skill: {failed_skill.skill_id}")

        if not self.ai_repairer:
            self.logger.warning("AI 修复器未配置，跳过自动修复")
            return failed_skill

        try:
            # 1. 分析错误
            analysis = await self.ai_repairer.analyze_error(failed_skill, error)
            self.logger.info(f"错误分析: {analysis[:100]}...")

            # 2. 生成修复版
            repaired = await self.ai_repairer.repair_skill(failed_skill, analysis)

            # 3. 验证修复结果
            valid = await self.ai_repairer.validate_repair(failed_skill, repaired)
            if not valid:
                self.logger.warning("修复结果校验失败，保留原版")
                return failed_skill

            # 4. 替换原文件
            self.skill_storage.save(repaired)
            self.logger.info(f"✅ Skill 修复完成: {repaired.skill_id} v{repaired.version}")
            return repaired

        except Exception as e:
            self.logger.error(f"自动修复失败: {e}")
            return failed_skill
