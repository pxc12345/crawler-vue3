package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserUpdateDTO {

    @Size(min = 2, max = 20, message = "用户名长度必须在2-20个字符之间")
    private String username;

    @Size(min = 6, max = 100, message = "密码长度必须在6-100个字符之间")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Size(max = 20, message = "手机号长度不能超过20个字符")
    private String phone;

    @Size(max = 50, message = "昵称长度不能超过50个字符")
    private String nickname;

    private Integer status;
}
