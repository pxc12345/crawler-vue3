package com.example.demo.exception;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ErrorCode {
    USER_NOT_FOUND("1001", "用户不存在"),
    USERNAME_ALREADY_EXISTS("1002", "用户名已存在"),
    EMAIL_ALREADY_EXISTS("1003", "邮箱已被注册"),
    INVALID_PARAMETER("2001", "参数无效"),
    BUSINESS_ERROR("3001", "业务处理异常"),
    SYSTEM_ERROR("5001", "系统异常");

    private final String code;
    private final String message;
}
