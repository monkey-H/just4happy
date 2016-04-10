# 编排和调度组件

nap的核心组件：
从 `compose.yml` (和 ) 解析整个项目的配置，按各service的依赖顺序生成service；
按特定调度策略将其部署到相应host上，调度策略还支持系统组件的特殊调度要求（如要求所有host上都要有一个运行实例）

除了由 `compose.yml` 指定初始的用户应用配置，运行时的状态信息则保存在 db （持久信息）和 consul 键值存储（非持久信息）中。

直接与 **容器** 相关的操作封装在 `container` 模块下

各容器的状态由 `health_check` 组件定期更新到 consul 中，但这不能及时响应容器的退出，以做出及时的的调度动作。
todo：需要实现容器生命周期的事件响应机制

**用户** 信息管理也在这里实现，但 **用户安全认证** 基于 `ldap` 实现

编排组件的个功能均提供 rest_api

## 参考
 + [docker compose](https://github.com/docker/compose/blob/release/docs/compose-file.md)
 + k8s [pod](http://kubernetes.io/docs/user-guide/pods/)，[service](http://kubernetes.io/docs/user-guide/services/)
